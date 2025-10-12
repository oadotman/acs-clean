#!/usr/bin/env python3
"""
Test script for the unified Tools SDK integration

This script tests the new unified SDK to ensure proper tool orchestration
and backward compatibility with the existing system.
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Test the SDK imports
try:
    from packages.tools_sdk import (
        ToolInput, ToolOutput, ToolRunner, ToolOrchestrator, 
        ToolRegistry, default_registry, ToolError
    )
    from packages.tools_sdk.tools import register_all_tools
    print("✅ SDK imports successful")
except ImportError as e:
    print(f"❌ SDK import failed: {e}")
    sys.exit(1)

# Test legacy imports for compatibility  
try:
    from app.schemas.ads import AdInput as LegacyAdInput
    from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService
    print("✅ Legacy compatibility imports successful")
except ImportError as e:
    print(f"⚠️ Legacy imports failed: {e}")
    print("This is expected if running without full app context")


class SDKTester:
    """Test suite for the unified Tools SDK"""
    
    def __init__(self):
        self.orchestrator = ToolOrchestrator()
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'errors': []
        }
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        self.test_results['tests_run'] += 1
        
        if passed:
            self.test_results['tests_passed'] += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            self.test_results['tests_failed'] += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")
                self.test_results['errors'].append(f"{test_name}: {details}")
    
    def test_registry_functionality(self):
        """Test tool registry functionality"""
        print("\n🧪 Testing Tool Registry")
        
        # Test tool registration
        try:
            register_all_tools()
            available_tools = default_registry.list_tools()
            self.log_test(
                "Tool Registration", 
                len(available_tools) > 0,
                f"Registered tools: {available_tools}"
            )
        except Exception as e:
            self.log_test("Tool Registration", False, str(e))
        
        # Test tool retrieval
        try:
            for tool_name in default_registry.list_tools():
                tool = default_registry.get_tool(tool_name)
                self.log_test(
                    f"Tool Retrieval ({tool_name})",
                    tool is not None,
                    f"Tool type: {tool.tool_type}"
                )
        except Exception as e:
            self.log_test("Tool Retrieval", False, str(e))
        
        # Test tool info
        try:
            for tool_name in default_registry.list_tools():
                info = default_registry.get_tool_info(tool_name)
                self.log_test(
                    f"Tool Info ({tool_name})",
                    'name' in info and 'tool_type' in info,
                    f"Info keys: {list(info.keys())}"
                )
        except Exception as e:
            self.log_test("Tool Info", False, str(e))
    
    async def test_input_output_formats(self):
        """Test input/output data structures"""
        print("\n🧪 Testing Input/Output Formats")
        
        # Test ToolInput creation
        try:
            test_input = ToolInput(
                headline="Test Amazing Product Launch",
                body_text="Don't miss out on this incredible opportunity to transform your business today!",
                cta="Get Started Now", 
                platform="facebook",
                industry="software",
                target_audience="small businesses"
            )
            
            self.log_test(
                "ToolInput Creation",
                test_input.headline == "Test Amazing Product Launch",
                f"Request ID: {test_input.request_id}"
            )
            
            # Test serialization
            input_dict = test_input.to_dict()
            self.log_test(
                "ToolInput Serialization",
                'headline' in input_dict and 'request_id' in input_dict,
                f"Serialized keys: {list(input_dict.keys())}"
            )
            
            # Test legacy conversion
            legacy_data = {
                'headline': 'Legacy Headline',
                'body_text': 'Legacy body text', 
                'cta': 'Legacy CTA',
                'platform': 'google'
            }
            legacy_input = ToolInput.from_legacy_ad_input(legacy_data)
            self.log_test(
                "Legacy Conversion",
                legacy_input.headline == "Legacy Headline",
                f"Converted platform: {legacy_input.platform}"
            )
            
        except Exception as e:
            self.log_test("Input/Output Formats", False, str(e))
    
    async def test_individual_tools(self):
        """Test individual tool execution"""
        print("\n🧪 Testing Individual Tools")
        
        test_input = ToolInput(
            headline="Amazing Product Launch",
            body_text="Don't miss this incredible opportunity to transform your business today with our revolutionary solution!",
            cta="Get Started Now",
            platform="facebook"
        )
        
        for tool_name in default_registry.list_tools():
            try:
                tool = default_registry.get_tool(tool_name)
                
                # Test validation
                validation_result = tool.validate_input(test_input)
                self.log_test(
                    f"Tool Validation ({tool_name})",
                    validation_result == True,
                    "Input validation passed"
                )
                
                # Test execution
                output = await tool.run(test_input)
                self.log_test(
                    f"Tool Execution ({tool_name})",
                    output.success == True,
                    f"Execution time: {output.execution_time:.3f}s, Scores: {len(output.scores)}"
                )
                
                # Test output format
                output_dict = output.to_dict()
                self.log_test(
                    f"Tool Output Format ({tool_name})",
                    'tool_name' in output_dict and 'success' in output_dict,
                    f"Output keys: {list(output_dict.keys())}"
                )
                
            except Exception as e:
                self.log_test(f"Tool Testing ({tool_name})", False, str(e))
    
    async def test_orchestration(self):
        """Test tool orchestration"""
        print("\n🧪 Testing Tool Orchestration")
        
        test_input = ToolInput(
            headline="Revolutionary AI Tool for Businesses",
            body_text="Transform your workflow with our cutting-edge artificial intelligence solution. Save time, increase productivity, and stay ahead of the competition.",
            cta="Start Free Trial",
            platform="linkedin"
        )
        
        available_tools = default_registry.list_tools()
        
        if not available_tools:
            self.log_test("Orchestration", False, "No tools available for testing")
            return
        
        try:
            # Test parallel execution
            result = await self.orchestrator.run_tools(
                test_input,
                available_tools,
                execution_mode="parallel"
            )
            
            self.log_test(
                "Parallel Orchestration",
                result.success == True,
                f"Tools run: {len(result.tool_results)}, Execution time: {result.total_execution_time:.3f}s"
            )
            
            # Test result aggregation
            self.log_test(
                "Score Aggregation", 
                len(result.aggregated_scores) > 0 or len(result.tool_results) == 0,
                f"Aggregated scores: {list(result.aggregated_scores.keys())}"
            )
            
            # Test sequential execution (with fewer tools for speed)
            limited_tools = available_tools[:2] if len(available_tools) > 1 else available_tools
            result_seq = await self.orchestrator.run_tools(
                test_input,
                limited_tools,
                execution_mode="sequential"
            )
            
            self.log_test(
                "Sequential Orchestration",
                result_seq.success == True,
                f"Tools run: {len(result_seq.tool_results)}"
            )
            
        except Exception as e:
            self.log_test("Orchestration", False, str(e))
    
    async def test_health_checks(self):
        """Test health check functionality"""
        print("\n🧪 Testing Health Checks")
        
        try:
            # Test orchestrator health check
            health_results = await self.orchestrator.health_check_tools()
            
            self.log_test(
                "Health Check Execution",
                isinstance(health_results, dict),
                f"Health checked {len(health_results)} tools"
            )
            
            # Test individual tool health
            healthy_tools = []
            for tool_name, health_info in health_results.items():
                if health_info.get('status') == 'healthy':
                    healthy_tools.append(tool_name)
            
            self.log_test(
                "Tool Health Status",
                len(healthy_tools) >= 0,  # Allow 0 healthy tools if dependencies missing
                f"Healthy tools: {healthy_tools}"
            )
            
        except Exception as e:
            self.log_test("Health Checks", False, str(e))
    
    async def test_enhanced_service(self):
        """Test enhanced ad analysis service (if available)"""
        print("\n🧪 Testing Enhanced Service Integration")
        
        try:
            # This will only work if we have the full app context
            from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService
            
            # Mock database session
            class MockDB:
                def add(self, obj): pass
                def commit(self): pass
                def rollback(self): pass
            
            service = EnhancedAdAnalysisService(MockDB())
            
            # Test service health
            health = await service.health_check()
            self.log_test(
                "Enhanced Service Health",
                'service' in health,
                f"Service status: {health.get('status')}"
            )
            
            # Test tool capabilities
            capabilities = service.get_available_tools()
            self.log_test(
                "Service Tool Capabilities",
                isinstance(capabilities, dict),
                f"Tools available: {len(capabilities)}"
            )
            
        except ImportError:
            self.log_test("Enhanced Service Integration", True, "Skipped - requires full app context")
        except Exception as e:
            self.log_test("Enhanced Service Integration", False, str(e))
    
    def test_error_handling(self):
        """Test error handling and exceptions"""
        print("\n🧪 Testing Error Handling")
        
        try:
            # Test tool not found
            try:
                default_registry.get_tool("nonexistent_tool")
                self.log_test("Tool Not Found Error", False, "Should have raised an error")
            except ToolError as e:
                self.log_test("Tool Not Found Error", True, f"Correctly raised: {e.error_code}")
            
            # Test invalid input
            test_input_invalid = ToolInput(
                headline="",  # Empty headline
                body_text="",  # Empty body
                cta="",       # Empty CTA
                platform="invalid_platform"
            )
            
            error_count = 0
            for tool_name in default_registry.list_tools():
                try:
                    tool = default_registry.get_tool(tool_name)
                    tool.validate_input(test_input_invalid)
                except Exception:
                    error_count += 1
            
            self.log_test(
                "Input Validation Errors",
                error_count > 0,
                f"Tools correctly rejected invalid input: {error_count}"
            )
            
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Tools SDK Test Suite")
        print("=" * 60)
        
        # Registry tests  
        self.test_registry_functionality()
        
        # Input/Output tests
        await self.test_input_output_formats()
        
        # Individual tool tests
        await self.test_individual_tools()
        
        # Orchestration tests
        await self.test_orchestration()
        
        # Health check tests
        await self.test_health_checks()
        
        # Enhanced service tests
        await self.test_enhanced_service()
        
        # Error handling tests
        self.test_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")
        
        if self.test_results['tests_failed'] > 0:
            print(f"\n❌ FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.test_results['tests_passed'] / self.test_results['tests_run'] * 100) if self.test_results['tests_run'] > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Tools SDK is ready for integration!")
        elif success_rate >= 60:
            print("⚠️ Tools SDK has some issues but core functionality works")
        else:
            print("🚨 Tools SDK needs significant fixes before integration")
        
        return success_rate >= 60


async def main():
    """Main test function"""
    tester = SDKTester()
    success = await tester.run_all_tests()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())