"""
Test script for team invitation with Resend integration.

This script tests the complete team invitation flow:
1. EmailService initialization with Resend API
2. Email template rendering
3. Sending test invitation email

Usage:
    python test_team_invitation_resend.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service import email_service
from app.core.config import settings


async def test_email_service_init():
    """Test that EmailService initializes correctly."""
    print("\n" + "="*60)
    print("Testing EmailService Initialization")
    print("="*60)

    if email_service._mock_mode:
        print("⚠️  WARNING: Running in MOCK MODE")
        print(f"   RESEND_API_KEY is {'NOT SET' if not settings.RESEND_API_KEY else 'SET'}")
        print(f"   Emails will be logged to console only")
    else:
        print("✅ EmailService initialized with Resend API")
        print(f"   API URL: {email_service.api_url}")
        print(f"   From Email: {settings.RESEND_FROM_EMAIL}")

    return True


async def test_template_rendering():
    """Test email template rendering."""
    print("\n" + "="*60)
    print("Testing Email Template Rendering")
    print("="*60)

    try:
        context = {
            'agency_name': 'Test Agency',
            'invited_by': 'John Doe',
            'role_name': 'Editor',
            'invitation_url': 'https://app.adcopysurge.com/invite/test-token',
            'personal_message': 'Welcome to our team!',
            'branding': {
                'app_name': 'AdCopySurge',
                'company_name': 'AdCopySurge',
                'primary_color': '#1976d2',
                'secondary_color': '#dc004e',
                'logo_url': 'https://app.adcopysurge.com/logo.png',
                'from_email': settings.RESEND_FROM_EMAIL,
                'support_email': settings.RESEND_FROM_EMAIL,
                'website_url': 'https://adcopysurge.com'
            },
            'current_year': 2025
        }

        # Test HTML template
        html_content = await email_service._render_template('team_invitation.html', context)
        print(f"✅ HTML template rendered successfully ({len(html_content)} chars)")

        # Test text template
        text_content = await email_service._render_template('team_invitation.txt', context)
        print(f"✅ Text template rendered successfully ({len(text_content)} chars)")

        return True

    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False


async def test_send_invitation():
    """Test sending an invitation email."""
    print("\n" + "="*60)
    print("Testing Team Invitation Email Sending")
    print("="*60)

    # You can change this to your test email
    test_email = input("\nEnter test email address (or press Enter to skip): ").strip()

    if not test_email:
        print("⏭️  Skipping email send test")
        return True

    try:
        result = await email_service.send_team_invitation(
            email=test_email,
            agency_name="Test Agency",
            invitation_token="test-token-12345",
            invited_by="Test User",
            role_name="Editor",
            personal_message="This is a test invitation from the automated test script."
        )

        if result.get('success'):
            print("✅ Invitation email sent successfully!")
            if result.get('mock_mode'):
                print("   (Mock mode - email was logged, not actually sent)")
            else:
                print(f"   Message ID: {result.get('message_id')}")
            return True
        else:
            print(f"❌ Failed to send email: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TEAM INVITATION RESEND INTEGRATION TEST")
    print("="*60)

    print(f"\nConfiguration:")
    print(f"  RESEND_API_KEY: {'✓ Set' if settings.RESEND_API_KEY else '✗ Not set'}")
    print(f"  RESEND_FROM_EMAIL: {settings.RESEND_FROM_EMAIL}")

    # Run tests
    results = []

    results.append(("EmailService Init", await test_email_service_init()))
    results.append(("Template Rendering", await test_template_rendering()))
    results.append(("Send Invitation", await test_send_invitation()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")

    return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
