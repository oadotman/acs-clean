"""
Platform Registry Service

Centralized service for loading, validating, and accessing platform-specific configurations.
Provides type-safe access to platform rules, character limits, and requirements.
"""
import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FieldConfig:
    """Configuration for a platform field (headline, body, cta, etc.)"""
    required: bool
    max_chars: int
    count: int = 1
    uniqueness: bool = False
    min_count: Optional[int] = None
    hook_length: Optional[int] = None
    includes_cta: bool = False

@dataclass
class PlatformConfig:
    """Complete configuration for a platform"""
    id: str
    display_name: str
    fields: Dict[str, FieldConfig]
    tone: str
    structure_order: List[str]
    special_requirements: List[str]
    cta_verbs: List[str]
    banned_phrases: List[str]
    repetition_rules: Dict[str, bool]
    hard_limits: bool
    audience_mindset: str

class PlatformRegistry:
    """Registry for managing platform configurations"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.platforms: Dict[str, PlatformConfig] = {}
        self.synonyms: Dict[str, str] = {}
        self.default_platform: str = "facebook"
        self._config_path = config_path or self._get_default_config_path()
        self._load_configurations()
    
    def _get_default_config_path(self) -> str:
        """Get the default path to platforms.json"""
        current_dir = Path(__file__).parent.parent.parent
        return str(current_dir / "config" / "platforms.json")
    
    def _load_configurations(self):
        """Load platform configurations from JSON file"""
        try:
            if not os.path.exists(self._config_path):
                raise FileNotFoundError(f"Platform config file not found: {self._config_path}")
            
            with open(self._config_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
            
            # Load metadata
            meta = config_data.get('_meta', {})
            self.synonyms = meta.get('synonyms', {})
            self.default_platform = meta.get('defaultPlatform', 'facebook')
            
            # Load platform configurations
            for platform_id, platform_data in config_data.items():
                if platform_id.startswith('_'):  # Skip metadata
                    continue
                
                self.platforms[platform_id] = self._parse_platform_config(platform_id, platform_data)
            
            logger.info(f"Loaded {len(self.platforms)} platform configurations")
            
        except Exception as e:
            logger.error(f"Failed to load platform configurations: {e}")
            raise RuntimeError(f"Platform registry initialization failed: {e}")
    
    def _parse_platform_config(self, platform_id: str, data: Dict[str, Any]) -> PlatformConfig:
        """Parse platform configuration from JSON data"""
        fields = {}
        for field_name, field_data in data.get('fields', {}).items():
            fields[field_name] = FieldConfig(
                required=field_data.get('required', False),
                max_chars=field_data.get('maxChars', 1000),
                count=field_data.get('count', 1),
                uniqueness=field_data.get('uniqueness', False),
                min_count=field_data.get('minCount'),
                hook_length=field_data.get('hookLength'),
                includes_cta=field_data.get('includesCTA', False)
            )
        
        return PlatformConfig(
            id=platform_id,
            display_name=data.get('displayName', platform_id.title()),
            fields=fields,
            tone=data.get('tone', ''),
            structure_order=data.get('structureOrder', []),
            special_requirements=data.get('specialRequirements', []),
            cta_verbs=data.get('ctaVerbs', []),
            banned_phrases=data.get('bannedPhrases', []),
            repetition_rules=data.get('repetitionRules', {}),
            hard_limits=data.get('hardLimits', True),
            audience_mindset=data.get('audienceMindset', '')
        )
    
    def get_platform_config(self, platform_id: str) -> Optional[PlatformConfig]:
        """Get platform configuration by ID"""
        normalized_id = self.resolve_platform_id(platform_id)
        return self.platforms.get(normalized_id)
    
    def resolve_platform_id(self, input_name: str) -> str:
        """Resolve platform name to canonical ID using synonyms"""
        if not input_name:
            return self.default_platform
        
        normalized_input = input_name.lower().strip()
        
        # Check direct match first
        if normalized_input in self.platforms:
            return normalized_input
        
        # Check synonyms
        if normalized_input in self.synonyms:
            return self.synonyms[normalized_input]
        
        # Return default if no match
        logger.warning(f"Unknown platform '{input_name}', using default '{self.default_platform}'")
        return self.default_platform
    
    def list_platforms(self) -> List[Dict[str, str]]:
        """List all available platforms"""
        return [
            {
                'id': config.id,
                'display_name': config.display_name,
                'tone': config.tone
            }
            for config in self.platforms.values()
        ]
    
    def validate_platform_content(self, platform_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content against platform requirements"""
        config = self.get_platform_config(platform_id)
        if not config:
            return {'valid': False, 'errors': [f'Unknown platform: {platform_id}']}
        
        errors = []
        warnings = []
        field_validations = {}
        
        for field_name, field_config in config.fields.items():
            field_value = content.get(field_name)
            field_validation = self._validate_field(field_name, field_value, field_config, config)
            field_validations[field_name] = field_validation
            
            if field_validation['errors']:
                errors.extend(field_validation['errors'])
            if field_validation['warnings']:
                warnings.extend(field_validation['warnings'])
        
        # Check for banned phrases
        banned_phrase_errors = self._check_banned_phrases(content, config.banned_phrases)
        errors.extend(banned_phrase_errors)
        
        # Check repetition rules
        repetition_errors = self._check_repetition_rules(content, config.repetition_rules)
        errors.extend(repetition_errors)
        
        return {
            'valid': len(errors) == 0,
            'platform_id': platform_id,
            'errors': errors,
            'warnings': warnings,
            'field_validations': field_validations
        }
    
    def _validate_field(self, field_name: str, field_value: Any, field_config: FieldConfig, platform_config: PlatformConfig) -> Dict[str, Any]:
        """Validate a single field"""
        errors = []
        warnings = []
        
        # Check if required field is present
        if field_config.required and not field_value:
            errors.append(f'{field_name} is required for {platform_config.display_name}')
            return {'errors': errors, 'warnings': warnings, 'char_count': 0, 'within_limit': False}
        
        if not field_value:
            return {'errors': errors, 'warnings': warnings, 'char_count': 0, 'within_limit': True}
        
        # Handle list fields (like headlines, hashtags)
        if isinstance(field_value, list):
            return self._validate_list_field(field_name, field_value, field_config, platform_config)
        
        # Handle string fields
        if isinstance(field_value, str):
            char_count = len(field_value)
            within_limit = char_count <= field_config.max_chars
            
            if not within_limit:
                if platform_config.hard_limits:
                    errors.append(f'{field_name} exceeds {field_config.max_chars} character limit ({char_count} chars)')
                else:
                    warnings.append(f'{field_name} exceeds recommended {field_config.max_chars} character limit ({char_count} chars)')
            
            return {
                'errors': errors,
                'warnings': warnings,
                'char_count': char_count,
                'within_limit': within_limit
            }
        
        return {'errors': errors, 'warnings': warnings, 'char_count': 0, 'within_limit': True}
    
    def _validate_list_field(self, field_name: str, field_value: List, field_config: FieldConfig, platform_config: PlatformConfig) -> Dict[str, Any]:
        """Validate list field (headlines, hashtags, etc.)"""
        errors = []
        warnings = []
        
        # Check count requirements
        if len(field_value) != field_config.count:
            if field_config.count > 1:
                errors.append(f'{field_name} requires exactly {field_config.count} items, got {len(field_value)}')
            elif field_config.min_count and len(field_value) < field_config.min_count:
                warnings.append(f'{field_name} should have at least {field_config.min_count} items')
        
        # Check individual item character limits
        total_chars = 0
        for i, item in enumerate(field_value):
            if isinstance(item, str):
                char_count = len(item)
                total_chars += char_count
                if char_count > field_config.max_chars:
                    errors.append(f'{field_name}[{i}] exceeds {field_config.max_chars} character limit ({char_count} chars)')
        
        # Check uniqueness for fields that require it
        if field_config.uniqueness and len(field_value) != len(set(field_value)):
            errors.append(f'{field_name} items must be unique - duplicates found')
        
        return {
            'errors': errors,
            'warnings': warnings,
            'char_count': total_chars,
            'within_limit': len(errors) == 0
        }
    
    def _check_banned_phrases(self, content: Dict[str, Any], banned_phrases: List[str]) -> List[str]:
        """Check content for banned phrases"""
        errors = []
        
        # Combine all text content
        all_text = ""
        for field_name, field_value in content.items():
            if isinstance(field_value, str):
                all_text += f" {field_value}"
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, str):
                        all_text += f" {item}"
        
        all_text = all_text.lower()
        
        for banned_phrase in banned_phrases:
            if banned_phrase.lower() in all_text:
                errors.append(f"Content contains banned phrase: '{banned_phrase}'")
        
        return errors
    
    def _check_repetition_rules(self, content: Dict[str, Any], repetition_rules: Dict[str, bool]) -> List[str]:
        """Check content against repetition rules"""
        errors = []
        
        if repetition_rules.get('preventHeadlineInBody', False):
            headline = content.get('headline', '')
            body = content.get('body', '')
            
            if headline and body and headline.lower() in body.lower():
                errors.append("Headline text should not be repeated in body copy")
        
        if repetition_rules.get('enforceHeadlineUniqueness', False):
            headlines = content.get('headlines', [])
            if headlines and len(headlines) != len(set([h.lower() for h in headlines])):
                errors.append("All headlines must be unique")
        
        return errors
    
    def get_character_limits(self, platform_id: str) -> Dict[str, int]:
        """Get character limits for all fields of a platform"""
        config = self.get_platform_config(platform_id)
        if not config:
            return {}
        
        limits = {}
        for field_name, field_config in config.fields.items():
            limits[field_name] = field_config.max_chars
        
        return limits
    
    def is_valid_platform(self, platform_id: str) -> bool:
        """Check if platform ID is valid"""
        return self.resolve_platform_id(platform_id) in self.platforms

# Global registry instance
_registry: Optional[PlatformRegistry] = None

def get_platform_registry() -> PlatformRegistry:
    """Get the global platform registry instance"""
    global _registry
    if _registry is None:
        _registry = PlatformRegistry()
    return _registry

def initialize_platform_registry(config_path: Optional[str] = None):
    """Initialize the global platform registry with custom config path"""
    global _registry
    _registry = PlatformRegistry(config_path)

# Convenience functions
def get_platform_config(platform_id: str) -> Optional[PlatformConfig]:
    """Get platform configuration"""
    return get_platform_registry().get_platform_config(platform_id)

def resolve_platform_id(platform_name: str) -> str:
    """Resolve platform name to canonical ID"""
    return get_platform_registry().resolve_platform_id(platform_name)

def validate_platform_content(platform_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content against platform requirements"""
    return get_platform_registry().validate_platform_content(platform_id, content)