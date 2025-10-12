#!/usr/bin/env python3
"""
AdCopySurge Environment Setup Script
Helps configure environment variables for development and production deployment.
"""

import os
import secrets
import string
from pathlib import Path


def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_env_file(template_path: str, output_path: str, replacements: dict = None):
    """Create .env file from template with optional replacements."""
    template_file = Path(template_path)
    output_file = Path(output_path)
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_path}")
        return False
    
    try:
        content = template_file.read_text(encoding='utf-8')
        
        if replacements:
            for old_value, new_value in replacements.items():
                content = content.replace(old_value, new_value)
        
        output_file.write_text(content, encoding='utf-8')
        print(f"✅ Created environment file: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating environment file: {e}")
        return False


def setup_development_environment():
    """Set up development environment."""
    print("\n🔧 Setting up DEVELOPMENT environment...")
    
    backend_dir = Path(__file__).parent / "backend"
    template_path = backend_dir / ".env.example"
    output_path = backend_dir / ".env"
    
    # Generate secure secret key for development
    secret_key = generate_secret_key(32)
    
    replacements = {
        "your-super-secret-key-change-this-in-production-min-32-chars": secret_key,
        "development": "development"  # Ensure it stays development
    }
    
    if create_env_file(str(template_path), str(output_path), replacements):
        print(f"🔑 Generated development SECRET_KEY: {secret_key[:8]}...")
        print("⚠️  Remember to update the following in your .env file:")
        print("   - DATABASE_URL (your local database)")
        print("   - REACT_APP_SUPABASE_URL and keys")
        print("   - OPENAI_API_KEY")
        print("   - RESEND_API_KEY (for email testing)")
        print("   - Other API keys as needed")
    

def setup_production_environment():
    """Set up production environment."""
    print("\n🚀 Setting up PRODUCTION environment...")
    
    backend_dir = Path(__file__).parent / "backend"
    template_path = backend_dir / ".env.production.template"
    output_path = backend_dir / ".env.production"
    
    # Generate secure secret key for production
    secret_key = generate_secret_key(64)  # Longer key for production
    
    replacements = {
        "CHANGE-THIS-SECURE-SECRET-KEY-MIN-32-CHARS-PRODUCTION-ONLY": secret_key,
    }
    
    if create_env_file(str(template_path), str(output_path), replacements):
        print(f"🔑 Generated production SECRET_KEY: {secret_key[:8]}...")
        print("\n🚨 CRITICAL: Update ALL production credentials in .env.production:")
        print("   ✅ DATABASE_URL (production database)")
        print("   ✅ SUPABASE_* (production Supabase project)")
        print("   ✅ OPENAI_API_KEY (production API key)")
        print("   ✅ RESEND_API_KEY (production email service)")
        print("   ✅ PADDLE_* (production payment processing)")
        print("   ✅ SENTRY_DSN (production error tracking)")
        print("   ✅ CORS_ORIGINS and ALLOWED_HOSTS (your domains)")
        print("   ✅ REDIS_URL (production Redis instance)")


def install_dependencies():
    """Install missing Python dependencies."""
    print("\n📦 Checking dependencies...")
    
    try:
        import resend
        print("✅ resend package is available")
    except ImportError:
        print("❌ resend package not found")
        print("Run: pip install resend==0.7.0")
    
    try:
        import jinja2
        print("✅ jinja2 package is available")
    except ImportError:
        print("❌ jinja2 package not found")
        print("Run: pip install jinja2>=3.1.2")


def main():
    """Main setup function."""
    print("🎯 AdCopySurge Environment Setup")
    print("=" * 50)
    
    print("\nWhat would you like to set up?")
    print("1. Development environment (.env)")
    print("2. Production environment (.env.production)")
    print("3. Check dependencies")
    print("4. All of the above")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        setup_development_environment()
    elif choice == "2":
        setup_production_environment()
    elif choice == "3":
        install_dependencies()
    elif choice == "4":
        setup_development_environment()
        setup_production_environment()
        install_dependencies()
    else:
        print("❌ Invalid choice. Exiting.")
        return
    
    print("\n✨ Setup completed!")
    print("\n📋 Next Steps:")
    print("1. Review and update your .env file(s) with actual credentials")
    print("2. Test email sending with: python -c 'from backend.app.services.email_service import email_service; print(\"Email service loaded successfully\")'")
    print("3. Run the application and test all integrations")
    print("4. Check the PRODUCTION_READINESS_AUDIT.md for launch checklist")


if __name__ == "__main__":
    main()