#!/usr/bin/env python3
"""
Test script to verify the Tools SDK fix
"""

import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Set environment variable for database URL (mock for testing)
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['OPENAI_API_KEY'] = 'test-key'

async def test_enhanced_service():
    """Test the enhanced service initialization"""
    
    try:
        # Import the enhanced service
        from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService
        from app.schemas.ads import AdInput
        
        print("✅ Successfully imported EnhancedAdAnalysisService")
        
        # Create a mock database session
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        
        # Initialize the service
        service = EnhancedAdAnalysisService(mock_db)
        print("✅ Successfully initialized EnhancedAdAnalysisService")
        
        # Check available tools
        available_tools = service.get_available_tools()
        print(f"✅ Available tools: {list(available_tools.keys())}")
        
        # Test health check
        health_status = await service.health_check()
        print(f"✅ Service health status: {health_status['status']}")
        print(f"✅ Healthy tools: {health_status['tools_healthy']}")
        
        # Test with sample ad data
        sample_ad = AdInput(
            headline="Test Headline",
            body_text="This is a test body text for our amazing product.",
            cta="Click Now",
            platform="facebook"
        )
        
        print("\n🧪 Testing analysis with sample ad...")
        
        # Test specific tools
        try:
            result = await service.analyze_with_specific_tools(
                user_id=1,
                ad=sample_ad,
                tool_names=["readability_analyzer"]
            )
            print("✅ Analysis completed successfully")
            print(f"✅ Tools executed: {list(result.get('tool_results', {}).keys())}")
            
            # Check if any tools returned results
            tool_results = result.get('tool_results', {})
            for tool_name, tool_output in tool_results.items():
                success = tool_output.get('success', False)
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"   {tool_name}: {status}")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    
    print("🔧 Testing Tools SDK Fix...")
    print("=" * 50)
    
    # Run the test
    success = asyncio.run(test_enhanced_service())
    
    if success:
        print("\n🎉 All tests passed! The Tools SDK fix should work.")
    else:
        print("\n💥 Tests failed. Check the errors above.")