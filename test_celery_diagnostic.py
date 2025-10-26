"""
Comprehensive Celery diagnostic
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_monitor.settings')
django.setup()

from django.conf import settings
from url_monitor.celery import app as celery_app
import redis

print("=" * 70)
print("CELERY CONFIGURATION DIAGNOSTIC")
print("=" * 70)

# 1. Check Django settings
print("\n1. DJANGO SETTINGS:")
print(f"   CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
print(f"   REDIS_URL: {getattr(settings, 'REDIS_URL', 'NOT SET')}")

# 2. Check Celery app configuration
print("\n2. CELERY APP CONFIGURATION:")
print(f"   Broker URL: {celery_app.conf.broker_url}")
print(f"   Result Backend: {celery_app.conf.result_backend}")

# 3. Test Redis connection
print("\n3. REDIS CONNECTION TEST:")
try:
    r = redis.from_url(settings.CELERY_BROKER_URL)
    r.ping()
    print("   ✓ Redis connection successful")
    
    # Check queue
    queue_length = r.llen('celery')
    print(f"   Queue length: {queue_length} tasks pending")
    
except Exception as e:
    print(f"   ✗ Redis connection FAILED: {e}")

# 4. List registered tasks
print("\n4. REGISTERED TASKS:")
registered_tasks = sorted(celery_app.tasks.keys())
for task in registered_tasks:
    if 'monitor' in task:
        print(f"   ✓ {task}")

# 5. Test task discovery
print("\n5. CHECKING TASK MODULE:")
try:
    from monitor import tasks
    print(f"   ✓ monitor.tasks module imported")
    print(f"   check_url_status: {tasks.check_url_status}")
    print(f"   schedule_checks: {tasks.schedule_checks}")
    print(f"   send_alert: {tasks.send_alert}")
except Exception as e:
    print(f"   ✗ Error importing tasks: {e}")

# 6. Send a test task and monitor queue
print("\n6. SENDING TEST TASK:")
from monitor.models import MonitoredURL
from monitor.tasks import check_url_status

urls = MonitoredURL.objects.filter(is_active=True)
if urls.exists():
    test_url = urls.first()
    print(f"   Testing URL: {test_url.name}")
    
    # Check queue before
    r = redis.from_url(settings.CELERY_BROKER_URL)
    before = r.llen('celery')
    print(f"   Queue before: {before} tasks")
    
    # Send task
    result = check_url_status.delay(str(test_url.id))
    print(f"   ✓ Task sent with ID: {result.id}")
    
    # Check queue after
    import time
    time.sleep(0.5)  # Give it a moment
    after = r.llen('celery')
    print(f"   Queue after: {after} tasks")
    
    if after > before:
        print("   ✓ Task is IN THE QUEUE waiting for worker!")
        print("\n   → PROBLEM: Worker is not consuming tasks from the queue")
        print("   → SOLUTION: Check your Celery Worker terminal:")
        print("     - Is it running?")
        print("     - Does it show 'Ready to accept tasks'?")
        print("     - Try restarting it: celery -A url_monitor worker --loglevel=info --pool=solo")
    else:
        print("   ✗ Task was NOT added to queue (or was consumed immediately)")
        print("   → If worker shows activity: SUCCESS!")
        print("   → If worker shows nothing: Check broker URL mismatch")
else:
    print("   ✗ No URLs to test")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
