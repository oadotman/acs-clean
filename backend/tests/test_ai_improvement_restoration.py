"""
Test AI-Powered Improvement Restoration

This test suite validates that the AI improvement generation system is working correctly
after the Phase 2 & 3 fixes.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService
from app.services.production_ai_generator import ProductionAIService
from app.schemas.ads import AdInput
from app.core.exceptions import fail_fast_on_mock_data, AIProviderUnavailable


class TestMockDataDetection:
    """Test Phase 2: Mock Data Detection Fix"""
    
    def test_allows_test_industry_input(self):
        """User input with 'Test' should be allowed"""
        test_data = {
            'headline': 'Great Product',
            'body_text': 'Amazing features',
            'industry': 'Test Industry',  # Should be allowed
            'platform': 'facebook'
        }
        
        # Set environment variable
        os.environ['ALLOW_TEST_DATA'] = 'true'
        
        # Should NOT raise exception
        try:
            fail_fast_on_mock_data(test_data, "test_input")
            assert True, "Test data was correctly allowed"
        except Exception as e:
            pytest.fail(f"Test data should be allowed but got error: {e}")
    
    def test_blocks_system_mocks(self):
        """System-level mock data should still be blocked"""
        mock_data = {
            'headline': 'mock_headline',  # System mock
            'body_text': 'template_response',  # System mock
            'industry': 'Real Industry',
            'platform': 'facebook'
        }
        
        # Should raise exception for system mocks
        with pytest.raises(Exception):
            fail_fast_on_mock_data(mock_data, "system_mock")
    
    def test_allows_demo_in_user_text(self):
        """User text containing 'demo' should be allowed"""
        test_data = {
            'headline': 'See our demo today',  # User text, not system mock
            'body_text': 'Try our demo product',
            'industry': 'SaaS',
            'platform': 'facebook'
        }
        
        os.environ['ALLOW_TEST_DATA'] = 'true'
        
        try:
            fail_fast_on_mock_data(test_data, "user_demo_text")
            assert True, "User demo text was correctly allowed"
        except Exception as e:
            pytest.fail(f"User demo text should be allowed but got error: {e}")


class TestAIServiceInitialization:
    """Test Phase 3: AI Service Integration"""
    
    def test_ai_service_initializes_with_valid_key(self):
        """ProductionAIService should initialize with valid OpenAI key"""
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not openai_key or not openai_key.startswith('sk-'):
            pytest.skip("No valid OpenAI API key found in environment")
        
        try:
            ai_service = ProductionAIService(openai_key, None)
            assert ai_service is not None
            assert 'openai' in ai_service.providers
        except Exception as e:
            pytest.fail(f"AI service should initialize with valid key: {e}")
    
    def test_enhanced_service_initializes_ai_service(self):
        """EnhancedAdAnalysisService should initialize ProductionAIService"""
        db_mock = Mock()
        
        # Mock environment variable
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test-key'}):
            try:
                service = EnhancedAdAnalysisService(db_mock)
                # Check that ai_service attribute exists (even if initialization failed)
                assert hasattr(service, 'ai_service')
            except Exception as e:
                pytest.fail(f"EnhancedAdAnalysisService should initialize: {e}")


class TestAlternativeGeneration:
    """Test Phase 3 & 4: AI-Powered Alternatives and A/B/C Variations"""
    
    @pytest.mark.asyncio
    async def test_generates_four_alternatives(self):
        """Should generate 1 improved + 3 A/B/C variations"""
        db_mock = Mock()
        
        # Create service
        service = EnhancedAdAnalysisService(db_mock)
        
        # Create test ad input
        test_ad = AdInput(
            headline="Flash Sale! 50% off",
            body_text="Limited time offer on all products",
            cta="Shop Now",
            platform="facebook",
            industry="Ecommerce",
            target_audience="Young adults"
        )
        
        # Mock AI service to return test alternatives
        mock_ai_result = {
            'headline': 'Improved Headline',
            'body_text': 'Improved body text',
            'cta': 'Improved CTA',
            'improvement_reason': 'Enhanced persuasion'
        }
        
        if service.ai_service:
            # If AI service is available, it should generate real alternatives
            with patch.object(service.ai_service, 'generate_ad_alternative', new=AsyncMock(return_value=mock_ai_result)):
                alternatives = await service._generate_fallback_alternatives(test_ad)
                
                assert len(alternatives) == 4, f"Expected 4 alternatives, got {len(alternatives)}"
                
                # Check variant types
                variant_types = [alt.variant_type for alt in alternatives]
                assert 'improved' in variant_types, "Should have 'improved' variant"
                assert 'variation_a_benefit' in variant_types, "Should have Variation A"
                assert 'variation_b_problem' in variant_types, "Should have Variation B"
                assert 'variation_c_story' in variant_types, "Should have Variation C"
        else:
            # If AI service not available, should return fallback
            alternatives = await service._generate_fallback_alternatives(test_ad)
            assert len(alternatives) == 1, "Fallback should return 1 alternative"
            assert alternatives[0].variant_type == 'fallback'
    
    @pytest.mark.asyncio
    async def test_alternatives_are_different_from_original(self):
        """Improved alternatives should differ from original ad"""
        db_mock = Mock()
        service = EnhancedAdAnalysisService(db_mock)
        
        test_ad = AdInput(
            headline="Original Headline",
            body_text="Original body text",
            cta="Original CTA",
            platform="facebook"
        )
        
        # Mock different AI results for each call
        mock_results = [
            {
                'headline': 'Improved Headline 1',
                'body_text': 'Improved body 1',
                'cta': 'CTA 1',
                'improvement_reason': 'Reason 1'
            },
            {
                'headline': 'Improved Headline 2',
                'body_text': 'Improved body 2',
                'cta': 'CTA 2',
                'improvement_reason': 'Reason 2'
            },
            {
                'headline': 'Improved Headline 3',
                'body_text': 'Improved body 3',
                'cta': 'CTA 3',
                'improvement_reason': 'Reason 3'
            },
            {
                'headline': 'Improved Headline 4',
                'body_text': 'Improved body 4',
                'cta': 'CTA 4',
                'improvement_reason': 'Reason 4'
            }
        ]
        
        call_count = 0
        async def mock_generate(*args, **kwargs):
            nonlocal call_count
            result = mock_results[call_count % len(mock_results)]
            call_count += 1
            return result
        
        if service.ai_service:
            with patch.object(service.ai_service, 'generate_ad_alternative', new=mock_generate):
                alternatives = await service._generate_fallback_alternatives(test_ad)
                
                for alt in alternatives:
                    # Check that improved text is different from original
                    assert alt.headline != test_ad.headline, "Headline should be different from original"
                    assert alt.body_text != test_ad.body_text, "Body should be different from original"
                    assert alt.cta != test_ad.cta, "CTA should be different from original"
    
    @pytest.mark.asyncio
    async def test_variations_have_distinct_strategies(self):
        """A/B/C variations should have different strategic approaches"""
        db_mock = Mock()
        service = EnhancedAdAnalysisService(db_mock)
        
        test_ad = AdInput(
            headline="Test Headline",
            body_text="Test body",
            cta="Test CTA",
            platform="facebook"
        )
        
        # Mock AI service
        mock_result = {
            'headline': 'Generated Headline',
            'body_text': 'Generated body',
            'cta': 'Generated CTA',
            'improvement_reason': 'AI-generated'
        }
        
        if service.ai_service:
            with patch.object(service.ai_service, 'generate_ad_alternative', new=AsyncMock(return_value=mock_result)):
                alternatives = await service._generate_fallback_alternatives(test_ad)
                
                # Find each variation type
                variation_a = next((a for a in alternatives if a.variant_type == 'variation_a_benefit'), None)
                variation_b = next((a for a in alternatives if a.variant_type == 'variation_b_problem'), None)
                variation_c = next((a for a in alternatives if a.variant_type == 'variation_c_story'), None)
                
                assert variation_a is not None, "Should have Variation A (Benefit-Focused)"
                assert variation_b is not None, "Should have Variation B (Problem-Focused)"
                assert variation_c is not None, "Should have Variation C (Story-Driven)"
                
                # Check improvement reasons describe strategies
                assert 'Benefit-Focused' in variation_a.improvement_reason
                assert 'Problem-Focused' in variation_b.improvement_reason
                assert 'Story-Driven' in variation_c.improvement_reason


class TestGracefulFallback:
    """Test graceful degradation when AI service unavailable"""
    
    @pytest.mark.asyncio
    async def test_fallback_when_ai_unavailable(self):
        """Should return fallback alternatives if AI service fails"""
        db_mock = Mock()
        
        # Create service with no AI key (will fail initialization)
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            service = EnhancedAdAnalysisService(db_mock)
            
            test_ad = AdInput(
                headline="Test",
                body_text="Test body",
                cta="Test CTA",
                platform="facebook"
            )
            
            alternatives = await service._generate_fallback_alternatives(test_ad)
            
            # Should return at least 1 fallback alternative
            assert len(alternatives) >= 1, "Should return fallback alternatives"
            
            # Check if it's a fallback
            if alternatives[0].variant_type == 'fallback':
                assert 'Fallback' in alternatives[0].improvement_reason or \
                       'unavailable' in alternatives[0].improvement_reason.lower()


class TestEndToEndWorkflow:
    """Test complete analysis workflow"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_analysis_workflow(self):
        """Test complete ad analysis from input to alternatives"""
        db_mock = Mock()
        service = EnhancedAdAnalysisService(db_mock)
        
        # Skip if no AI service available
        if not service.ai_service:
            pytest.skip("AI service not available for integration test")
        
        test_ad = AdInput(
            headline="🔥 Flash Sale Today!",
            body_text="Get 50% off all products. Limited time only!",
            cta="Shop Now",
            platform="facebook",
            industry="Ecommerce",
            target_audience="Budget-conscious shoppers"
        )
        
        # Note: This would call real AI API if OPENAI_API_KEY is set
        # For actual testing, you'd want to mock this or use a test account
        try:
            # Mock the analysis to avoid real API calls in tests
            with patch.object(service.orchestrator, 'run_tools', new=AsyncMock(return_value=Mock(
                success=True,
                overall_score=75.0,
                tool_results={},
                request_id='test-123',
                total_execution_time=1.0,
                to_dict=lambda: {}
            ))):
                # Mock AI alternative generation
                mock_ai_result = {
                    'headline': 'Exclusive Flash Sale: Save Big Today! 🎯',
                    'body_text': 'Transform your shopping experience with 50% off sitewide. This incredible deal won\'t last!',
                    'cta': 'Claim Your Discount',
                    'improvement_reason': 'Enhanced urgency and value proposition'
                }
                
                with patch.object(service.ai_service, 'generate_ad_alternative', new=AsyncMock(return_value=mock_ai_result)):
                    result = await service.analyze_ad(
                        user_id=1,
                        ad=test_ad,
                        competitor_ads=[],
                        requested_tools=None
                    )
                    
                    # Verify response structure
                    assert result is not None
                    assert hasattr(result, 'alternatives')
                    assert len(result.alternatives) > 0
                    
                    # Verify alternatives are not just prefixed originals
                    for alt in result.alternatives:
                        if alt.variant_type != 'fallback':
                            # Check that it's not just "Improved: {original}"
                            assert not alt.headline.startswith("Improved: "), \
                                "Headline should not just be prefixed with 'Improved:'"
                            assert not alt.body_text.startswith("Enhanced version: "), \
                                "Body should not just be prefixed with 'Enhanced version:'"
        
        except AIProviderUnavailable as e:
            pytest.skip(f"AI provider unavailable: {e}")


def run_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("AI-POWERED IMPROVEMENT RESTORATION - TEST SUITE")
    print("="*70 + "\n")
    
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-W', 'ignore::DeprecationWarning'
    ])


if __name__ == '__main__':
    run_tests()
