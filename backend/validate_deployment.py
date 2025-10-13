#!/usr/bin/env python3
"""
AdCopySurge Deployment Validation Script
Validates the application is ready for production deployment
"""

import sys
import os
import importlib.util
from pathlib import Path
import json
from typing import List, Dict, Any

class DeploymentValidator:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed_checks = []
        
    def log_issue(self, message: str):
        """Log a critical issue that would prevent deployment"""
        self.issues.append(message)
        print(f"❌ ISSUE: {message}")
        
    def log_warning(self, message: str):
        """Log a warning that should be addressed"""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")
        
    def log_pass(self, message: str):
        """Log a successful check"""
        self.passed_checks.append(message)
        print(f"✅ PASS: {message}")

    def check_python_version(self):
        """Verify Python version compatibility"""
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor == 11:
            self.log_pass(f"Python version {python_version.major}.{python_version.minor}.{python_version.micro} is compatible with target VPS")
        elif python_version.major == 3 and python_version.minor >= 11:
            self.log_warning(f"Using Python {python_version.major}.{python_version.minor}.{python_version.micro}, target VPS uses 3.11")
        else:
            self.log_issue(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} not compatible with Python 3.11 target")

    def check_main_import(self):
        """Test if main.py can be imported"""
        try:
            # Add current directory to path
            sys.path.insert(0, '.')
            import main
            if hasattr(main, 'app'):
                self.log_pass("Main application imports successfully")
                if hasattr(main.app, 'title'):
                    self.log_pass(f"FastAPI app found: {main.app.title}")
                else:
                    self.log_warning("FastAPI app found but no title attribute")
            else:
                self.log_issue("main.py imports but no 'app' attribute found")
        except ImportError as e:
            self.log_issue(f"Cannot import main.py: {e}")
        except Exception as e:
            self.log_issue(f"Error importing main.py: {e}")

    def check_requirements_file(self):
        """Check if requirements.txt exists and is valid"""
        req_file = Path("requirements.txt")
        if req_file.exists():
            self.log_pass("requirements.txt exists")
            try:
                with open(req_file, 'r') as f:
                    lines = f.readlines()
                    packages = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
                    self.log_pass(f"Found {len(packages)} packages in requirements.txt")
                    
                    # Check for critical packages
                    critical_packages = ['fastapi', 'uvicorn', 'gunicorn', 'sqlalchemy', 'pydantic']
                    for pkg in critical_packages:
                        if any(pkg in line.lower() for line in packages):
                            self.log_pass(f"Critical package found: {pkg}")
                        else:
                            self.log_warning(f"Critical package not found in requirements: {pkg}")
            except Exception as e:
                self.log_issue(f"Error reading requirements.txt: {e}")
        else:
            self.log_issue("requirements.txt not found")

    def check_gunicorn_config(self):
        """Check if gunicorn.conf.py exists and is valid"""
        gunicorn_file = Path("gunicorn.conf.py")
        if gunicorn_file.exists():
            self.log_pass("gunicorn.conf.py exists")
            try:
                with open(gunicorn_file, 'r') as f:
                    content = f.read()
                    if 'bind' in content:
                        self.log_pass("Gunicorn bind configuration found")
                    else:
                        self.log_warning("No bind configuration in gunicorn.conf.py")
                    
                    if 'workers' in content:
                        self.log_pass("Gunicorn workers configuration found")
                    else:
                        self.log_warning("No workers configuration in gunicorn.conf.py")
            except Exception as e:
                self.log_issue(f"Error reading gunicorn.conf.py: {e}")
        else:
            self.log_issue("gunicorn.conf.py not found")

    def check_init_files(self):
        """Check if all necessary __init__.py files exist"""
        required_init_files = [
            Path("app/__init__.py"),
            Path("app/api/__init__.py"),
            Path("app/core/__init__.py"),
            Path("app/models/__init__.py"),
        ]
        
        for init_file in required_init_files:
            if init_file.exists():
                self.log_pass(f"__init__.py found: {init_file}")
            else:
                self.log_issue(f"Missing __init__.py: {init_file}")

    def check_environment_template(self):
        """Check if environment configuration is documented"""
        env_example = Path(".env.example")
        env_file = Path(".env")
        
        if env_example.exists():
            self.log_pass(".env.example found")
        else:
            self.log_warning(".env.example not found - create one for deployment reference")
            
        if env_file.exists():
            self.log_warning(".env file exists - ensure it's not committed to version control")
        else:
            self.log_pass("No .env file found in repository (good for security)")

    def check_blog_references(self):
        """Check if blog references have been removed"""
        main_file = Path("main.py")
        if main_file.exists():
            try:
                with open(main_file, 'r') as f:
                    content = f.read()
                    if 'blog' in content.lower():
                        self.log_warning("Blog references still found in main.py")
                    else:
                        self.log_pass("No blog references in main.py")
            except Exception as e:
                self.log_warning(f"Could not check main.py for blog references: {e}")

    def check_duplicate_requirements(self):
        """Check for multiple requirements files that might cause confusion"""
        req_files = list(Path('.').glob('requirements*.txt'))
        if len(req_files) == 1:
            self.log_pass("Only one requirements file found")
        elif len(req_files) > 1:
            self.log_warning(f"Multiple requirements files found: {[f.name for f in req_files]}")
            self.log_warning("Consider consolidating to single requirements.txt")

    def check_frontend_supabase_client(self):
        """Check if Supabase client file exists"""
        supabase_client = Path("../frontend/lib/supabaseClientClean.js")
        if supabase_client.exists():
            self.log_pass("Frontend Supabase client found")
        else:
            self.log_issue("Frontend Supabase client not found at ../frontend/lib/supabaseClientClean.js")

    def generate_report(self) -> Dict[str, Any]:
        """Generate a deployment readiness report"""
        total_checks = len(self.issues) + len(self.warnings) + len(self.passed_checks)
        
        report = {
            "deployment_ready": len(self.issues) == 0,
            "total_checks": total_checks,
            "passed": len(self.passed_checks),
            "warnings": len(self.warnings),
            "issues": len(self.issues),
            "critical_issues": self.issues,
            "warnings_list": self.warnings,
            "passed_checks": self.passed_checks
        }
        
        return report

    def run_all_checks(self):
        """Run all deployment validation checks"""
        print("🔍 Running AdCopySurge Deployment Validation...\n")
        
        self.check_python_version()
        self.check_main_import()
        self.check_requirements_file()
        self.check_gunicorn_config()
        self.check_init_files()
        self.check_environment_template()
        self.check_blog_references()
        self.check_duplicate_requirements()
        self.check_frontend_supabase_client()
        
        print("\n" + "="*60)
        print("DEPLOYMENT VALIDATION REPORT")
        print("="*60)
        
        report = self.generate_report()
        
        print(f"Total Checks: {report['total_checks']}")
        print(f"✅ Passed: {report['passed']}")
        print(f"⚠️  Warnings: {report['warnings']}")
        print(f"❌ Issues: {report['issues']}")
        
        if report['deployment_ready']:
            print("\n🎉 DEPLOYMENT READY! No critical issues found.")
            print("Address warnings before deploying to production.")
        else:
            print("\n🚨 DEPLOYMENT NOT READY! Critical issues must be fixed first.")
            print("\nCritical Issues to Fix:")
            for issue in self.issues:
                print(f"  - {issue}")
        
        if self.warnings:
            print("\nWarnings to Address:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        return report

if __name__ == "__main__":
    validator = DeploymentValidator()
    report = validator.run_all_checks()
    
    # Save report to file
    with open("deployment_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: deployment_validation_report.json")
    
    # Exit with appropriate code
    sys.exit(0 if report['deployment_ready'] else 1)