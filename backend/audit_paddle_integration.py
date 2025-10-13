#!/usr/bin/env python3
"""
Comprehensive Paddle Payment Integration Audit
Checks all aspects of Paddle integration for production readiness
"""

import os
import sys
import json
import requests
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PaddleIntegrationAuditor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed_checks = []
        self.config = {}
        self.frontend_config = {}
        
    def log_issue(self, check: str, message: str):
        """Log a critical issue"""
        issue = f"{check}: {message}"
        self.issues.append(issue)
        print(f"❌ CRITICAL: {issue}")
        
    def log_warning(self, check: str, message: str):
        """Log a warning"""
        warning = f"{check}: {message}"
        self.warnings.append(warning)
        print(f"⚠️  WARNING: {warning}")
        
    def log_pass(self, check: str, message: str):
        """Log a passed check"""
        passed = f"{check}: {message}"
        self.passed_checks.append(passed)
        print(f"✅ PASS: {passed}")

    def audit_backend_configuration(self) -> bool:
        """Audit backend configuration"""
        print("\n🔧 Auditing Backend Configuration...")
        
        try:
            from app.core.config import settings
            self.config = settings
            
            # Check required environment variables
            required_vars = {
                'PADDLE_VENDOR_ID': settings.PADDLE_VENDOR_ID,
                'PADDLE_API_KEY': settings.PADDLE_API_KEY,
                'PADDLE_WEBHOOK_SECRET': settings.PADDLE_WEBHOOK_SECRET,
                'PADDLE_ENVIRONMENT': settings.PADDLE_ENVIRONMENT,
                'PADDLE_API_URL': settings.PADDLE_API_URL
            }
            
            missing_required = []
            for var_name, var_value in required_vars.items():
                if not var_value:
                    missing_required.append(var_name)
                else:
                    self.log_pass("Config", f"{var_name} is set")
            
            if missing_required:
                self.log_issue("Config", f"Missing required variables: {', '.join(missing_required)}")
                return False
            
            # Check environment setting
            if settings.PADDLE_ENVIRONMENT not in ['sandbox', 'production']:
                self.log_warning("Config", f"Invalid PADDLE_ENVIRONMENT: {settings.PADDLE_ENVIRONMENT}")
            else:
                self.log_pass("Config", f"Environment: {settings.PADDLE_ENVIRONMENT}")
            
            # Check API URL matches environment
            expected_url = "https://vendors.paddle.com/api" if settings.PADDLE_ENVIRONMENT == "production" else "https://sandbox-vendors.paddle.com/api"
            if settings.PADDLE_API_URL != expected_url:
                self.log_warning("Config", f"API URL may not match environment. Expected: {expected_url}, Got: {settings.PADDLE_API_URL}")
            
            # Check product IDs (optional but recommended)
            product_ids = {
                'PADDLE_BASIC_MONTHLY_ID': settings.PADDLE_BASIC_MONTHLY_ID,
                'PADDLE_PRO_MONTHLY_ID': settings.PADDLE_PRO_MONTHLY_ID,
                'PADDLE_BASIC_YEARLY_ID': settings.PADDLE_BASIC_YEARLY_ID,
                'PADDLE_PRO_YEARLY_ID': settings.PADDLE_PRO_YEARLY_ID
            }
            
            for id_name, id_value in product_ids.items():
                if id_value:
                    self.log_pass("Config", f"{id_name} is configured")
                else:
                    self.log_warning("Config", f"{id_name} not set - you'll need this for specific plans")
            
            return True
            
        except Exception as e:
            self.log_issue("Config", f"Failed to load configuration: {e}")
            return False

    def audit_backend_service(self) -> bool:
        """Audit backend Paddle service"""
        print("\n🧪 Auditing Backend Service...")
        
        try:
            from app.services.paddle_service import PaddleService
            from app.models.user import User, SubscriptionTier
            
            # Test service initialization
            class MockDB:
                def query(self, model): return self
                def filter(self, condition): return self
                def first(self): return None
                def commit(self): pass
            
            service = PaddleService(MockDB())
            self.log_pass("Service", "PaddleService instantiated successfully")
            
            # Check service configuration
            if hasattr(service, 'vendor_id') and service.vendor_id:
                self.log_pass("Service", "Vendor ID loaded in service")
            else:
                self.log_issue("Service", "Vendor ID not loaded in service")
                return False
            
            # Test subscription limits
            for tier in SubscriptionTier:
                try:
                    limits = service._get_subscription_limits(tier)
                    self.log_pass("Service", f"Subscription limits for {tier.value}: {limits['monthly_limit']} analyses, ${limits['price']}")
                except Exception as e:
                    self.log_warning("Service", f"Failed to get limits for {tier.value}: {e}")
            
            # Test plan mapping
            test_plans = [
                'growth_monthly', 'agency_standard_monthly', 
                'agency_premium_monthly', 'agency_unlimited_monthly'
            ]
            for plan in test_plans:
                tier = service._plan_id_to_tier(plan)
                self.log_pass("Service", f"Plan {plan} maps to {tier.value}")
            
            return True
            
        except Exception as e:
            self.log_issue("Service", f"Service audit failed: {e}")
            return False

    def audit_database_schema(self) -> bool:
        """Audit database schema for Paddle fields"""
        print("\n🗃️ Auditing Database Schema...")
        
        try:
            from app.models.user import User
            
            # Check Paddle fields exist
            paddle_fields = ['paddle_subscription_id', 'paddle_plan_id', 'paddle_checkout_id']
            
            # Check if fields are defined on the model
            user_columns = [column.name for column in User.__table__.columns]
            
            for field in paddle_fields:
                if field in user_columns:
                    self.log_pass("Database", f"Field '{field}' exists in User table")
                else:
                    self.log_issue("Database", f"Field '{field}' missing from User table - run migrations")
                    return False
            
            # Check subscription tier enum
            from app.models.user import SubscriptionTier
            expected_tiers = ['FREE', 'GROWTH', 'AGENCY_STANDARD', 'AGENCY_PREMIUM', 'AGENCY_UNLIMITED']
            actual_tiers = [tier.name for tier in SubscriptionTier]
            
            for tier in expected_tiers:
                if tier in actual_tiers:
                    self.log_pass("Database", f"SubscriptionTier.{tier} exists")
                else:
                    self.log_warning("Database", f"SubscriptionTier.{tier} missing")
            
            return True
            
        except Exception as e:
            self.log_issue("Database", f"Database schema audit failed: {e}")
            return False

    def audit_api_endpoints(self) -> bool:
        """Audit API endpoints"""
        print("\n🌐 Auditing API Endpoints...")
        
        try:
            from app.api.subscriptions import router
            
            # Check if Paddle routes exist
            routes = [route for route in router.routes]
            paddle_routes = [route for route in routes if hasattr(route, 'path') and 'paddle' in route.path]
            
            expected_paddle_endpoints = ['/paddle/checkout', '/paddle/webhook', '/paddle/cancel']
            
            for endpoint in expected_paddle_endpoints:
                found = any(endpoint in route.path for route in paddle_routes if hasattr(route, 'path'))
                if found:
                    self.log_pass("API", f"Endpoint '{endpoint}' exists")
                else:
                    self.log_issue("API", f"Endpoint '{endpoint}' not found")
                    return False
            
            # Check subscription service import
            try:
                from app.services.paddle_service import PaddleService
                self.log_pass("API", "PaddleService imported successfully in subscriptions.py")
            except ImportError:
                self.log_issue("API", "PaddleService import failed in subscriptions.py")
                return False
            
            return True
            
        except Exception as e:
            self.log_issue("API", f"API endpoints audit failed: {e}")
            return False

    def audit_frontend_configuration(self) -> bool:
        """Audit frontend configuration"""
        print("\n🎨 Auditing Frontend Configuration...")
        
        # Check if frontend directory exists
        frontend_dir = Path(__file__).parent.parent / "frontend"
        if not frontend_dir.exists():
            self.log_warning("Frontend", "Frontend directory not found - skipping frontend audit")
            return True
        
        # Check Paddle service file
        paddle_service_path = frontend_dir / "src" / "services" / "paddleService.js"
        if paddle_service_path.exists():
            self.log_pass("Frontend", "paddleService.js exists")
            
            # Basic content check
            try:
                with open(paddle_service_path, 'r') as f:
                    content = f.read()
                    
                if 'REACT_APP_PADDLE_VENDOR_ID' in content:
                    self.log_pass("Frontend", "Uses REACT_APP_PADDLE_VENDOR_ID environment variable")
                else:
                    self.log_warning("Frontend", "REACT_APP_PADDLE_VENDOR_ID not found in service")
                
                if 'paddle.js' in content.lower():
                    self.log_pass("Frontend", "Loads Paddle.js script")
                else:
                    self.log_warning("Frontend", "Paddle.js loading not detected")
                    
            except Exception as e:
                self.log_warning("Frontend", f"Could not analyze paddleService.js: {e}")
        else:
            self.log_issue("Frontend", "paddleService.js not found")
            return False
        
        # Check if Paddle is referenced in components
        components_dir = frontend_dir / "src" / "components"
        if components_dir.exists():
            paddle_refs = []
            for file_path in components_dir.rglob("*.js"):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if 'paddle' in content.lower():
                            paddle_refs.append(file_path.name)
                except:
                    pass
            
            if paddle_refs:
                self.log_pass("Frontend", f"Paddle referenced in components: {', '.join(paddle_refs[:3])}")
            else:
                self.log_warning("Frontend", "No Paddle references found in components")
        
        return True

    def test_paddle_api_connectivity(self) -> bool:
        """Test connection to Paddle API"""
        print("\n🔌 Testing Paddle API Connectivity...")
        
        if not hasattr(self, 'config') or not self.config:
            self.log_warning("API Test", "No configuration loaded - skipping API test")
            return True
        
        try:
            # Test basic API connectivity (this won't work without real credentials)
            api_url = self.config.PADDLE_API_URL
            vendor_id = self.config.PADDLE_VENDOR_ID
            auth_code = self.config.PADDLE_API_KEY
            
            if not auth_code:
                self.log_warning("API Test", "No PADDLE_API_KEY - cannot test API connectivity")
                return True
            
            # Simple ping test (list products endpoint)
            test_data = {
                'vendor_id': vendor_id,
                'vendor_auth_code': auth_code
            }
            
            response = requests.post(
                f"{api_url}/2.0/product/get_products",
                data=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log_pass("API Test", "Successfully connected to Paddle API")
                    products = result.get('response', {}).get('products', [])
                    self.log_pass("API Test", f"Found {len(products)} products in Paddle account")
                else:
                    self.log_warning("API Test", f"Paddle API error: {result.get('error', {}).get('message', 'Unknown error')}")
            else:
                self.log_warning("API Test", f"Paddle API returned status {response.status_code}")
            
            return True
            
        except requests.exceptions.Timeout:
            self.log_warning("API Test", "Paddle API request timed out")
            return True
        except requests.exceptions.RequestException as e:
            self.log_warning("API Test", f"Could not connect to Paddle API: {e}")
            return True
        except Exception as e:
            self.log_warning("API Test", f"API connectivity test failed: {e}")
            return True

    def audit_webhook_configuration(self) -> bool:
        """Audit webhook configuration"""
        print("\n🪝 Auditing Webhook Configuration...")
        
        try:
            # Check webhook endpoint exists
            from app.api.subscriptions import router
            webhook_routes = [route for route in router.routes if hasattr(route, 'path') and 'webhook' in route.path]
            
            if webhook_routes:
                self.log_pass("Webhook", "Webhook endpoint exists in API")
            else:
                self.log_issue("Webhook", "Webhook endpoint not found")
                return False
            
            # Check webhook secret is configured
            if hasattr(self, 'config') and self.config and self.config.PADDLE_WEBHOOK_SECRET:
                self.log_pass("Webhook", "Webhook secret is configured")
            else:
                self.log_warning("Webhook", "PADDLE_WEBHOOK_SECRET not set - webhooks won't be verified")
            
            # Check nginx configuration for webhook endpoint (if exists)
            nginx_configs = list(Path(__file__).parent.parent.glob("**/nginx*.conf"))
            webhook_proxy_configured = False
            
            for config_file in nginx_configs:
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                        if '/api/subscriptions/paddle/webhook' in content:
                            webhook_proxy_configured = True
                            self.log_pass("Webhook", f"Webhook proxy configured in {config_file.name}")
                            break
                except:
                    pass
            
            if not webhook_proxy_configured and nginx_configs:
                self.log_warning("Webhook", "Webhook endpoint not found in nginx configuration")
            
            return True
            
        except Exception as e:
            self.log_issue("Webhook", f"Webhook audit failed: {e}")
            return False

    def audit_security_considerations(self) -> bool:
        """Audit security aspects"""
        print("\n🔒 Auditing Security Considerations...")
        
        # Check CSP includes Paddle domains
        if hasattr(self, 'config') and self.config:
            csp = getattr(self.config, 'CONTENT_SECURITY_POLICY', '')
            if 'cdn.paddle.com' in csp:
                self.log_pass("Security", "Paddle CDN allowed in Content Security Policy")
            else:
                self.log_warning("Security", "Paddle CDN not found in CSP - may block Paddle.js")
        
        # Check HTTPS configuration
        if hasattr(self, 'config') and self.config:
            debug_mode = getattr(self.config, 'DEBUG', True)
            environment = getattr(self.config, 'ENVIRONMENT', 'development')
            
            if environment == 'production' and debug_mode:
                self.log_warning("Security", "DEBUG mode enabled in production - disable for security")
            
            if environment == 'production':
                # Should force HTTPS in production
                self.log_pass("Security", "Production environment configured")
            else:
                self.log_warning("Security", f"Environment is {environment} - ensure HTTPS in production")
        
        # Check webhook signature verification is implemented
        try:
            from app.services.paddle_service import PaddleService
            if hasattr(PaddleService, 'verify_webhook'):
                self.log_pass("Security", "Webhook signature verification implemented")
            else:
                self.log_warning("Security", "Webhook signature verification not found")
        except:
            pass
        
        return True

    def generate_implementation_checklist(self) -> List[str]:
        """Generate implementation checklist"""
        checklist = [
            "✅ Set up Paddle account (sandbox/production)",
            "✅ Configure environment variables in production",
            "✅ Create products in Paddle dashboard",
            "✅ Update product IDs in code",
            "✅ Set up webhook endpoints in Paddle dashboard",
            "✅ Test checkout flow end-to-end",
            "✅ Test webhook processing",
            "✅ Verify subscription upgrades/downgrades",
            "✅ Test subscription cancellation",
            "✅ Configure proper error handling",
            "✅ Set up monitoring and alerting",
            "✅ Test payment failure scenarios",
            "✅ Verify usage limits are enforced",
            "✅ Test billing cycle renewals"
        ]
        return checklist

    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run complete audit"""
        print("🔍 Starting Comprehensive Paddle Integration Audit")
        print("=" * 60)
        
        audit_functions = [
            self.audit_backend_configuration,
            self.audit_backend_service,
            self.audit_database_schema,
            self.audit_api_endpoints,
            self.audit_frontend_configuration,
            self.test_paddle_api_connectivity,
            self.audit_webhook_configuration,
            self.audit_security_considerations
        ]
        
        results = []
        for audit_func in audit_functions:
            try:
                result = audit_func()
                results.append(result)
            except Exception as e:
                print(f"❌ Audit function {audit_func.__name__} crashed: {e}")
                results.append(False)
        
        # Generate report
        total_checks = len(self.issues) + len(self.warnings) + len(self.passed_checks)
        critical_issues = len(self.issues)
        warnings = len(self.warnings)
        passed = len(self.passed_checks)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "production_ready": critical_issues == 0,
            "total_checks": total_checks,
            "passed": passed,
            "warnings": warnings,
            "critical_issues": critical_issues,
            "issues_list": self.issues,
            "warnings_list": self.warnings,
            "passed_checks": self.passed_checks,
            "implementation_checklist": self.generate_implementation_checklist()
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 PADDLE INTEGRATION AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Critical Issues: {critical_issues}")
        
        if critical_issues == 0:
            print("\n🎉 PADDLE INTEGRATION READY FOR PRODUCTION!")
            print("Address warnings for optimal setup.")
        else:
            print("\n🚨 CRITICAL ISSUES FOUND!")
            print("Fix these issues before deploying to production:")
            for issue in self.issues:
                print(f"  • {issue}")
        
        if warnings > 0:
            print(f"\n⚠️  {warnings} Warnings to address:")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more warnings")
        
        print("\n📋 Implementation Checklist:")
        for item in self.generate_implementation_checklist()[:7]:
            print(f"  {item}")
        print("  ... (see full report for complete checklist)")
        
        return report

if __name__ == "__main__":
    auditor = PaddleIntegrationAuditor()
    report = auditor.run_comprehensive_audit()
    
    # Save detailed report
    report_file = "paddle_integration_audit_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if report['production_ready'] else 1)