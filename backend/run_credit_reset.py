#!/usr/bin/env python3
"""
Standalone script to run monthly credit reset
Can be called from cron or systemd timer

Add to crontab:
0 0 1 * * cd /opt/adcopysurge/backend && /opt/adcopysurge/backend/venv/bin/python run_credit_reset.py >> /var/log/adcopysurge/credit_reset.log 2>&1
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tasks.credit_reset import reset_all_user_credits, cleanup_expired_idempotency_keys


if __name__ == "__main__":
    print(f"Starting credit reset task at {os.popen('date').read().strip()}")

    # Run monthly credit reset
    result = reset_all_user_credits()

    if result.get('success'):
        print(f"✅ Credit reset completed successfully")
        print(f"   Total users: {result.get('total')}")
        print(f"   Successful: {result.get('successful')}")
        print(f"   Failed: {result.get('failed')}")
    else:
        print(f"❌ Credit reset failed: {result.get('error')}")
        sys.exit(1)

    # Run cleanup task
    print("\nRunning idempotency key cleanup...")
    cleanup_result = cleanup_expired_idempotency_keys()

    if cleanup_result.get('success'):
        print(f"✅ Cleanup completed: {cleanup_result.get('deleted')} keys deleted")
    else:
        print(f"❌ Cleanup failed: {cleanup_result.get('error')}")

    print(f"\nCompleted at {os.popen('date').read().strip()}")
