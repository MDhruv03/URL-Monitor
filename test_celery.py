"""
Quick test to verify Celery is working
Run with: python test_celery.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_monitor.settings')
django.setup()

from monitor.tasks import check_url_status
from monitor.models import MonitoredURL

print("=" * 60)
print("CELERY CONNECTION TEST")
print("=" * 60)

# Check if we have any URLs
urls = MonitoredURL.objects.filter(is_active=True)
print(f"\n✓ Found {urls.count()} active URLs in database")

if urls.exists():
    test_url = urls.first()
    print(f"\n✓ Testing with URL: {test_url.name} ({test_url.url})")
    print(f"  URL ID: {test_url.id}")
    
    print("\n→ Sending task to Celery worker...")
    result = check_url_status.delay(str(test_url.id))
    
    print(f"✓ Task queued successfully!")
    print(f"  Task ID: {result.id}")
    print("\n→ Check your Celery WORKER terminal - you should see:")
    print("  [INFO/MainProcess] Task monitor.tasks.check_url_status[...]")
    print("  [INFO/MainProcess] Task monitor.tasks.check_url_status[...] succeeded")
else:
    print("\n⚠ No active URLs found. Please add a URL first:")
    print("  1. Go to http://127.0.0.1:8000/")
    print("  2. Login and add a URL to monitor")
    print("  3. Run this test again")

print("\n" + "=" * 60)
