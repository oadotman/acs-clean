#!/usr/bin/env python3
"""
Security Audit Script for AdCopySurge
Performs comprehensive security checks on the application
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class SecurityAuditor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        self.base_path = Path(__file__).parent

    def add_issue(self, category: str, description: str, severity: str = "HIGH"):
        self.issues.append({
            "category": category,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })

    def add_warning(self, category: str, description: str):
        self.warnings.append({
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })

    def add_passed(self, category: str, description: str):
        self.passed.append({
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })

    def check_environment_files(self):
        """Check for exposed environment files"""
        print("[*] Checking for exposed environment files...")

        env_files = [
            ".env",
            ".env.local",
            ".env.production",
            "backend/.env",
            "frontend/.env"
        ]

        for env_file in env_files:
            file_path = self.base_path / env_file
            if file_path.exists():
                # Check if it's in gitignore
                gitignore_path = self.base_path / ".gitignore"
                if gitignore_path.exists():
                    with open(gitignore_path, 'r') as f:
                        gitignore_content = f.read()
                        if env_file not in gitignore_content:
                            self.add_issue("Environment", f"{env_file} not in .gitignore", "CRITICAL")
                        else:
                            self.add_passed("Environment", f"{env_file} properly ignored")

                # Check for sensitive keys
                with open(file_path, 'r') as f:
                    content = f.read()

                    # Check for real API keys patterns
                    if re.search(r'sk-[a-zA-Z0-9]{48,}', content):
                        self.add_issue("Secrets", f"Potential API key exposed in {env_file}", "CRITICAL")

                    if re.search(r'(password|secret|key)\s*=\s*["\']?[a-zA-Z0-9]{20,}', content, re.IGNORECASE):
                        self.add_warning("Secrets", f"Potential secret in {env_file}")

    def check_dependencies(self):
        """Check for vulnerable dependencies"""
        print("[*] Checking dependencies for vulnerabilities...")

        # Check Python dependencies
        if (self.base_path / "backend" / "requirements.txt").exists():
            try:
                # Check for outdated packages
                result = subprocess.run(
                    ["pip", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    cwd=self.base_path / "backend"
                )

                if result.returncode == 0:
                    outdated = json.loads(result.stdout)
                    if len(outdated) > 10:
                        self.add_warning("Dependencies", f"{len(outdated)} Python packages are outdated")
                    else:
                        self.add_passed("Dependencies", "Python packages reasonably up to date")

            except Exception as e:
                self.add_warning("Dependencies", f"Could not check Python dependencies: {e}")

        # Check Node dependencies
        if (self.base_path / "frontend" / "package.json").exists():
            try:
                # Check with npm audit (if available)
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.base_path / "frontend"
                )

                if result.returncode == 0:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("metadata", {}).get("vulnerabilities", {})

                    if vulnerabilities.get("high", 0) > 0 or vulnerabilities.get("critical", 0) > 0:
                        self.add_issue("Dependencies",
                                     f"npm audit found {vulnerabilities.get('critical', 0)} critical and "
                                     f"{vulnerabilities.get('high', 0)} high vulnerabilities",
                                     "HIGH")
                    elif vulnerabilities.get("moderate", 0) > 0:
                        self.add_warning("Dependencies",
                                       f"npm audit found {vulnerabilities.get('moderate', 0)} moderate vulnerabilities")
                    else:
                        self.add_passed("Dependencies", "No high/critical npm vulnerabilities found")

            except Exception as e:
                self.add_warning("Dependencies", f"Could not run npm audit: {e}")

    def check_security_headers(self):
        """Check security headers configuration"""
        print("[*] Checking security headers configuration...")

        headers_file = self.base_path / "backend" / "app" / "middleware" / "security_headers.py"
        if headers_file.exists():
            with open(headers_file, 'r') as f:
                content = f.read()

                # Check for important headers
                important_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "X-XSS-Protection",
                    "Strict-Transport-Security",
                    "Content-Security-Policy"
                ]

                for header in important_headers:
                    if header in content:
                        self.add_passed("Security Headers", f"{header} is configured")
                    else:
                        self.add_warning("Security Headers", f"{header} might not be configured")

    def check_authentication(self):
        """Check authentication configuration"""
        print("[*] Checking authentication configuration...")

        # Check for JWT configuration
        config_file = self.base_path / "backend" / "app" / "core" / "config.py"
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()

                # Check for secure defaults
                if "BYPASS_AUTH_IN_DEV" in content:
                    self.add_warning("Authentication", "Development auth bypass flag found - ensure it's disabled in production")

                if re.search(r'ACCESS_TOKEN_EXPIRE_MINUTES\s*=\s*(\d+)', content):
                    self.add_passed("Authentication", "Token expiration configured")

                if "SUPABASE_JWT_SECRET" in content:
                    self.add_passed("Authentication", "Supabase JWT verification configured")

    def check_database_security(self):
        """Check database security configurations"""
        print("[*] Checking database security...")

        # Check for SQL injection prevention
        backend_path = self.base_path / "backend" / "app"

        vulnerable_patterns = [
            r'f".*SELECT.*{.*}.*"',  # f-string in SQL
            r'%\s*\(.*\).*SELECT',    # % formatting in SQL
            r'\.format\(.*SELECT'      # .format in SQL
        ]

        sql_files = list(backend_path.rglob("*.py"))
        vulnerable_files = []

        for file_path in sql_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    for pattern in vulnerable_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            vulnerable_files.append(str(file_path.relative_to(self.base_path)))
                            break
            except:
                pass

        if vulnerable_files:
            self.add_issue("SQL Injection", f"Potential SQL injection in: {', '.join(vulnerable_files[:3])}", "CRITICAL")
        else:
            self.add_passed("SQL Injection", "No obvious SQL injection vulnerabilities found")

    def check_credit_system(self):
        """Check credit system security"""
        print("[*] Checking credit system security...")

        credit_service = self.base_path / "backend" / "app" / "services" / "credit_service.py"
        if credit_service.exists():
            with open(credit_service, 'r') as f:
                content = f.read()

                # Check for atomic operations
                if "WHERE current_credits >=" in content:
                    self.add_passed("Credit System", "Atomic credit operations implemented")
                else:
                    self.add_issue("Credit System", "Credit operations may not be atomic", "HIGH")

                # Check for refund mechanism
                if "def refund_credits" in content:
                    self.add_passed("Credit System", "Credit refund mechanism exists")
                else:
                    self.add_issue("Credit System", "No credit refund mechanism found", "HIGH")

                # Check for transaction logging
                if "credit_transactions" in content:
                    self.add_passed("Credit System", "Credit transaction logging implemented")

    def check_rate_limiting(self):
        """Check rate limiting configuration"""
        print("[*] Checking rate limiting...")

        rate_limit_file = self.base_path / "backend" / "app" / "middleware" / "rate_limiter.py"
        if rate_limit_file.exists():
            self.add_passed("Rate Limiting", "Rate limiting middleware found")

            with open(rate_limit_file, 'r') as f:
                content = f.read()
                if "redis" in content.lower():
                    self.add_passed("Rate Limiting", "Redis-based rate limiting configured")

        else:
            self.add_warning("Rate Limiting", "Rate limiting middleware not found")

    def check_csrf_protection(self):
        """Check CSRF protection"""
        print("[*] Checking CSRF protection...")

        csrf_file = self.base_path / "backend" / "app" / "middleware" / "csrf_protection.py"
        if csrf_file.exists():
            with open(csrf_file, 'r') as f:
                content = f.read()

                # Check for exempted critical endpoints
                if '"/api/ads/analyze"' in content and 'exempt_paths' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if '"/api/ads/analyze"' in line:
                            # Check if it's in the exempt_paths section
                            for j in range(max(0, i-10), min(len(lines), i+10)):
                                if 'exempt_paths' in lines[j]:
                                    self.add_issue("CSRF", "Critical endpoint /api/ads/analyze may be exempt from CSRF", "HIGH")
                                    break
                            else:
                                self.add_passed("CSRF", "/api/ads/analyze endpoint protected by CSRF")
                else:
                    self.add_passed("CSRF", "CSRF protection configured")

    def check_webhook_security(self):
        """Check webhook signature validation"""
        print("[*] Checking webhook security...")

        paddle_service = self.base_path / "backend" / "app" / "services" / "paddle_service.py"
        if paddle_service.exists():
            with open(paddle_service, 'r') as f:
                content = f.read()

                if "def verify_webhook_signature" in content:
                    if "hmac.compare_digest" in content:
                        self.add_passed("Webhooks", "Webhook signature validation with constant-time comparison")
                    else:
                        self.add_warning("Webhooks", "Webhook signature validation exists but may be vulnerable to timing attacks")
                else:
                    self.add_issue("Webhooks", "No webhook signature validation found", "CRITICAL")

    def check_logging(self):
        """Check for sensitive data in logs"""
        print("[*] Checking logging configuration...")

        # Check for password/token logging
        backend_files = list((self.base_path / "backend").rglob("*.py"))

        sensitive_log_patterns = [
            r'log.*password',
            r'log.*secret',
            r'log.*api_key',
            r'print.*password',
            r'print.*secret'
        ]

        files_with_sensitive_logs = []

        for file_path in backend_files[:50]:  # Check first 50 files for performance
            try:
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    for pattern in sensitive_log_patterns:
                        if re.search(pattern, content):
                            files_with_sensitive_logs.append(str(file_path.relative_to(self.base_path)))
                            break
            except:
                pass

        if files_with_sensitive_logs:
            self.add_warning("Logging", f"Potential sensitive data logging in {len(files_with_sensitive_logs)} files")
        else:
            self.add_passed("Logging", "No obvious sensitive data logging found")

    def generate_report(self):
        """Generate security audit report"""
        print("\n" + "="*80)
        print("SECURITY AUDIT REPORT - AdCopySurge")
        print("="*80)
        print(f"Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

        # Summary
        total_issues = len(self.issues)
        critical_issues = len([i for i in self.issues if i['severity'] == 'CRITICAL'])
        high_issues = len([i for i in self.issues if i['severity'] == 'HIGH'])

        print("[SUMMARY] SUMMARY")
        print("-" * 40)
        print(f"[PASS] Passed Checks: {len(self.passed)}")
        print(f"[WARN]  Warnings: {len(self.warnings)}")
        print(f"[FAIL] Issues Found: {total_issues}")
        print(f"   - Critical: {critical_issues}")
        print(f"   - High: {high_issues}")
        print(f"   - Medium/Low: {total_issues - critical_issues - high_issues}")

        # Critical Issues
        if critical_issues > 0:
            print("\n[CRITICAL] CRITICAL ISSUES (Must Fix Before Production)")
            print("-" * 40)
            for issue in [i for i in self.issues if i['severity'] == 'CRITICAL']:
                print(f"• [{issue['category']}] {issue['description']}")

        # High Priority Issues
        if high_issues > 0:
            print("\n[WARN]  HIGH PRIORITY ISSUES")
            print("-" * 40)
            for issue in [i for i in self.issues if i['severity'] == 'HIGH']:
                print(f"• [{issue['category']}] {issue['description']}")

        # Warnings
        if self.warnings:
            print("\n[NOTE] WARNINGS")
            print("-" * 40)
            for warning in self.warnings[:10]:  # Show first 10
                print(f"• [{warning['category']}] {warning['description']}")

        # Passed Checks
        print("\n[PASS] PASSED CHECKS")
        print("-" * 40)
        for passed in self.passed[:15]:  # Show first 15
            print(f"• [{passed['category']}] {passed['description']}")

        # Calculate Security Score
        total_checks = len(self.passed) + len(self.warnings) + len(self.issues)
        if total_checks > 0:
            security_score = (len(self.passed) / total_checks) * 100

            # Penalties for critical issues
            security_score -= critical_issues * 10
            security_score -= high_issues * 5
            security_score = max(0, security_score)

            print("\n" + "="*80)
            print(f"[SCORE] SECURITY SCORE: {security_score:.1f}%")
            print("="*80)

            if security_score >= 90:
                print("[PASS] Excellent security posture - Ready for production")
            elif security_score >= 75:
                print("[WARN]  Good security with minor issues - Address before production")
            elif security_score >= 60:
                print("[WARN]  Moderate security concerns - Significant improvements needed")
            else:
                print("[FAIL] Poor security posture - NOT ready for production")

        return {
            "score": security_score if total_checks > 0 else 0,
            "issues": self.issues,
            "warnings": self.warnings,
            "passed": self.passed
        }

def main():
    auditor = SecurityAuditor()

    print("Starting Security Audit for AdCopySurge...")
    print("-" * 80)

    # Run all checks
    auditor.check_environment_files()
    auditor.check_dependencies()
    auditor.check_security_headers()
    auditor.check_authentication()
    auditor.check_database_security()
    auditor.check_credit_system()
    auditor.check_rate_limiting()
    auditor.check_csrf_protection()
    auditor.check_webhook_security()
    auditor.check_logging()

    # Generate report
    result = auditor.generate_report()

    # Save report to file
    report_file = Path("security_audit_report.json")
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\n[FILE] Full report saved to: {report_file}")

    # Exit with appropriate code
    if result["score"] < 60 or any(i["severity"] == "CRITICAL" for i in result["issues"]):
        sys.exit(1)  # Failed audit
    else:
        sys.exit(0)  # Passed audit

if __name__ == "__main__":
    main()