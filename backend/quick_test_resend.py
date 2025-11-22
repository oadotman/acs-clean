"""
Quick test for Resend integration without loading full app config.
"""

import asyncio
import httpx
import os


async def test_resend_api():
    """Test Resend API directly."""
    print("\n" + "="*60)
    print("QUICK RESEND API TEST")
    print("="*60)

    # Get API key from environment
    api_key = os.getenv('RESEND_API_KEY')
    from_email = os.getenv('RESEND_FROM_EMAIL', 'noreply@adcopysurge.com')

    if not api_key:
        print("\n⚠️  RESEND_API_KEY not set in environment")
        print("   Please export RESEND_API_KEY=your_api_key")
        print("   Or add it to your .env file")
        return False

    print(f"\n✅ RESEND_API_KEY found: {api_key[:10]}...")
    print(f"✅ FROM_EMAIL: {from_email}")

    # Get test email
    test_email = input("\nEnter test email address (or press Enter to skip): ").strip()

    if not test_email:
        print("\n⏭️  Skipping actual email send test")
        print("   Test completed - configuration looks good!")
        return True

    print(f"\n📧 Sending test email to {test_email}...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.resend.com/emails',
                json={
                    "from": from_email,
                    "to": [test_email],
                    "subject": "Test Email from AdCopySurge",
                    "html": """
                        <html>
                        <body style="font-family: Arial, sans-serif; padding: 20px;">
                            <h2>Test Email</h2>
                            <p>This is a test email from the AdCopySurge Resend integration.</p>
                            <p>If you received this, your Resend integration is working correctly!</p>
                        </body>
                        </html>
                    """,
                    "text": "This is a test email from the AdCopySurge Resend integration."
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                print("\n✅ Email sent successfully!")
                print(f"   Message ID: {result.get('id')}")
                print(f"   Check {test_email} for the test email")
                return True
            else:
                print(f"\n❌ Resend API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_resend_api())
        if success:
            print("\n🎉 Resend integration test passed!")
        else:
            print("\n⚠️  Resend integration test failed")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
