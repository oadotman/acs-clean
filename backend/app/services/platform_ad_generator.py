"""
Platform-Driven Ad Generation Service

Orchestrates the complete platform-aware ad generation pipeline including
parsing, prompt building, LLM calls with structured output, validation, and sanitization.
"""
import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import asdict
from openai import AsyncOpenAI

from .platform_registry import get_platform_config, resolve_platform_id
from .platform_aware_parser import PlatformAwareParser, ParsedAd
from .platform_prompt_builder import PlatformPromptBuilder
from .content_validator import ContentValidator, ValidationResult

logger = logging.getLogger(__name__)

class GenerationResult:
    """Result of ad generation process"""
    
    def __init__(self):
        self.success: bool = False
        self.platform_id: str = ""
        self.generated_content: Dict[str, Any] = {}
        self.char_counts: Dict[str, int] = {}
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.generation_report: Dict[str, Any] = {}

class PlatformAdGenerator:
    """Platform-aware ad generation orchestrator"""
    
    def __init__(self, openai_api_key: str, temperature_config: Optional[Dict[str, float]] = None):
        self.openai_api_key = openai_api_key
        self.client = AsyncOpenAI(api_key=openai_api_key)
        
        # Platform-specific temperature settings
        self.temperature_config = temperature_config or {
            'facebook': 0.7,
            'instagram': 0.8,
            'google_ads': 0.3,  # Lower for precision and uniqueness
            'linkedin': 0.5,
            'twitter_x': 0.8,
            'tiktok': 0.9
        }
        
        # Initialize components
        self.parser = PlatformAwareParser()
        self.prompt_builder = PlatformPromptBuilder()
        self.validator = ContentValidator()
        
        # Configuration
        self.max_retries = 3  # Increased for quality gating
        self.timeout_seconds = 30
        self.min_confidence_score = 60  # Only show output above this score
    
    async def generate_ad(self, 
                         text_input: str, 
                         platform_id: str, 
                         context: Optional[Dict[str, Any]] = None) -> GenerationResult:
        """Main generation method - orchestrates the complete pipeline"""
        
        start_time = time.time()
        result = GenerationResult()
        
        try:
            # Step 1: Resolve platform ID and validate
            resolved_platform_id = resolve_platform_id(platform_id)
            platform_config = get_platform_config(resolved_platform_id)
            
            if not platform_config:
                result.errors.append(f"Unsupported platform: {platform_id}")
                return result
            
            result.platform_id = resolved_platform_id
            logger.info(f"Starting generation for platform: {resolved_platform_id}")
            
            # Step 2: Parse input with platform-aware parser
            parsed_ad = self.parser.parse_ad(text_input, resolved_platform_id)
            
            # Step 3: Build platform-specific prompt
            prompt_dict = self.prompt_builder.build_prompt(resolved_platform_id, parsed_ad, context)
            
            # Step 4: Generate content with LLM (with retry logic)
            generated_content = await self._generate_with_retries(
                resolved_platform_id, prompt_dict, parsed_ad, context
            )
            
            if not generated_content:
                result.errors.append("LLM generation failed after all retries")
                return result
            
            # Step 5: Final validation and sanitization with quality gating
            validation_result = self.validator.validate_and_sanitize(
                generated_content, resolved_platform_id, strict_mode=True
            )
            
            # Quality gating: only accept content with confidence score >= 60
            if validation_result.confidence_score >= self.min_confidence_score:
                result.success = True
                result.generated_content = validation_result.sanitized_content
                result.char_counts = validation_result.char_counts
                result.warnings = validation_result.warnings
            else:
                # Low quality - add to errors and potentially retry
                quality_error = f"Quality score too low: {validation_result.confidence_score}/100 (minimum: {self.min_confidence_score})"
                result.errors.append(quality_error)
                result.warnings = validation_result.warnings
                # Still return sanitized content for fallback
                result.generated_content = validation_result.sanitized_content
                result.char_counts = validation_result.char_counts
            
            # Step 6: Build metrics and report
            end_time = time.time()
            result.metrics = {
                'generation_time_ms': round((end_time - start_time) * 1000, 2),
                'platform_id': resolved_platform_id,
                'parsing_confidence': parsed_ad.confidence,
                'validation_passed': validation_result.is_valid,
                'retry_count': getattr(self, '_last_retry_count', 0),
                'input_char_count': len(text_input),
                'total_warnings': len(result.warnings),
                'total_errors': len(result.errors)
            }
            
            result.generation_report = {
                'platform_config_used': resolved_platform_id,
                'parsing_method': parsed_ad.parsing_report.get('method', 'unknown'),
                'parsing_report': parsed_ad.parsing_report,
                'validation_report': validation_result.validation_report,
                'prompt_template_id': f"{resolved_platform_id}_structured",
                'character_limits_enforced': platform_config.hard_limits
            }
            
            logger.info(f"Generation completed for {resolved_platform_id}: success={result.success}, time={result.metrics['generation_time_ms']}ms")
            
        except Exception as e:
            logger.exception(f"Generation failed for {platform_id}: {str(e)}")
            result.errors.append(f"Generation failed: {str(e)}")
            result.metrics = {
                'generation_time_ms': round((time.time() - start_time) * 1000, 2),
                'error': str(e)
            }
        
        return result
    
    async def _generate_with_retries(self, 
                                   platform_id: str, 
                                   prompt_dict: Dict[str, str],
                                   parsed_ad: ParsedAd,
                                   context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate content with retry logic for validation failures"""
        
        self._last_retry_count = 0
        
        for attempt in range(self.max_retries + 1):
            try:
                # Call LLM with structured output
                generated_content = await self._call_llm_structured(platform_id, prompt_dict)
                
                if not generated_content:
                    logger.warning(f"LLM returned empty content for {platform_id}, attempt {attempt + 1}")
                    continue
                
                # Quick validation check with confidence scoring
                validation_result = self.validator.validate_and_sanitize(
                    generated_content, platform_id, strict_mode=False
                )
                
                logger.info(f"Generation attempt {attempt + 1} for {platform_id}: confidence={validation_result.confidence_score}/100")
                
                # Quality gating: check both validity and confidence score
                meets_quality = validation_result.confidence_score >= self.min_confidence_score
                
                # If quality is good or this is the last attempt, return result
                if meets_quality or attempt == self.max_retries:
                    if not meets_quality and attempt == self.max_retries:
                        logger.warning(f"Final attempt for {platform_id} still below quality threshold: {validation_result.confidence_score}/100")
                    return generated_content
                
                # Create retry prompt with detailed feedback
                retry_feedback = self.validator.create_retry_feedback(validation_result)
                if retry_feedback:
                    logger.info(f"Retrying generation for {platform_id} (attempt {attempt + 2}): score={validation_result.confidence_score}, issues={len(validation_result.errors + validation_result.quality_issues)}")
                    # Update prompt with retry feedback
                    prompt_dict['user'] += f"\n\n{retry_feedback}"
                    self._last_retry_count += 1
                
            except Exception as e:
                logger.warning(f"LLM call failed for {platform_id}, attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries:
                    raise
                continue
        
        return None
    
    async def _call_llm_structured(self, platform_id: str, prompt_dict: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Call OpenAI with structured JSON output"""
        
        temperature = self.temperature_config.get(platform_id, 0.7)
        
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": prompt_dict['system']},
                        {"role": "user", "content": prompt_dict['user']}
                    ],
                    response_format={"type": "json_object"},
                    temperature=temperature,
                    max_tokens=1000,
                    timeout=self.timeout_seconds
                ),
                timeout=self.timeout_seconds
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                parsed_content = json.loads(content)
                return parsed_content
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response for {platform_id}: {e}")
                logger.debug(f"Raw response: {content}")
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"LLM request timeout for {platform_id}")
            return None
        except Exception as e:
            logger.error(f"LLM request failed for {platform_id}: {str(e)}")
            return None
    
    async def generate_batch(self, 
                           requests: List[Dict[str, Any]]) -> List[GenerationResult]:
        """Generate ads for multiple platforms in parallel"""
        
        logger.info(f"Starting batch generation for {len(requests)} requests")
        
        # Create tasks for parallel execution
        tasks = []
        for req in requests:
            task = self.generate_ad(
                text_input=req.get('text_input', ''),
                platform_id=req.get('platform_id', 'facebook'),
                context=req.get('context', {})
            )
            tasks.append(task)
        
        # Execute in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Batch generation failed: {str(e)}")
            # Return error results for all requests
            error_results = []
            for req in requests:
                error_result = GenerationResult()
                error_result.platform_id = req.get('platform_id', 'unknown')
                error_result.errors.append(f"Batch generation failed: {str(e)}")
                error_results.append(error_result)
            return error_results
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = GenerationResult()
                error_result.platform_id = requests[i].get('platform_id', 'unknown')
                error_result.errors.append(f"Generation failed: {str(result)}")
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        logger.info(f"Batch generation completed: {sum(1 for r in processed_results if r.success)}/{len(processed_results)} successful")
        
        return processed_results
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the generator"""
        return {
            'service': 'platform_ad_generator',
            'status': 'healthy',
            'openai_configured': bool(self.openai_api_key),
            'max_retries': self.max_retries,
            'timeout_seconds': self.timeout_seconds,
            'temperature_config': self.temperature_config,
            'supported_platforms': list(self.temperature_config.keys())
        }

# Convenience function for single generation
async def generate_platform_ad(text_input: str, 
                             platform_id: str, 
                             openai_api_key: str,
                             context: Optional[Dict[str, Any]] = None) -> GenerationResult:
    """Generate a single platform-specific ad"""
    generator = PlatformAdGenerator(openai_api_key)
    return await generator.generate_ad(text_input, platform_id, context)