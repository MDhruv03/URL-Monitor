#!/usr/bin/env python
"""
Quick diagnostic script to check Django ALLOWED_HOSTS configuration
Run this in Render Shell to debug 400 Bad Request errors
"""

import os
import sys

print("\n" + "="*60)
print("  DJANGO ALLOWED_HOSTS DIAGNOSTIC")
print("="*60 + "\n")

# Check if Django is available
try:
    import django
    from django.conf import settings
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_monitor.settings')
    django.setup()
    
    print("✅ Django imported successfully\n")
    
    # Check DEBUG mode
    print(f"DEBUG Mode: {settings.DEBUG}")
    if settings.DEBUG:
        print("  ⚠️  DEBUG is True - should be False in production!\n")
    else:
        print("  ✅ DEBUG is False (correct for production)\n")
    
    # Check ALLOWED_HOSTS
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
        print("  ❌ ALLOWED_HOSTS is empty or set to ['*']")
    elif 'url-monitor-2xlk.onrender.com' in settings.ALLOWED_HOSTS:
        print("  ✅ Render domain is in ALLOWED_HOSTS")
    else:
        print("  ❌ Render domain NOT in ALLOWED_HOSTS")
        print("     Missing: url-monitor-2xlk.onrender.com")
    
    print("\n" + "-"*60)
    
    # Check environment variables
    print("\nEnvironment Variables:")
    print("-"*60)
    
    allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', 'NOT SET')
    print(f"ALLOWED_HOSTS env var: {allowed_hosts_env}")
    
    if allowed_hosts_env == 'NOT SET':
        print("  ❌ ALLOWED_HOSTS environment variable is NOT set!")
        print("     GO TO RENDER DASHBOARD → ENVIRONMENT → ADD THIS:")
        print("     Key:   ALLOWED_HOSTS")
        print("     Value: url-monitor-2xlk.onrender.com")
    
    database_url = os.environ.get('DATABASE_URL', 'NOT SET')
    if database_url != 'NOT SET':
        print(f"✅ DATABASE_URL is set")
    else:
        print(f"❌ DATABASE_URL is NOT set")
    
    redis_url = os.environ.get('REDIS_URL', 'NOT SET')
    if redis_url != 'NOT SET':
        print(f"✅ REDIS_URL is set")
    else:
        print(f"❌ REDIS_URL is NOT set")
    
    print("\n" + "="*60)
    print("  RECOMMENDATION")
    print("="*60)
    
    if 'url-monitor-2xlk.onrender.com' not in settings.ALLOWED_HOSTS:
        print("""
🔧 TO FIX 400 BAD REQUEST:

1. Go to: https://dashboard.render.com
2. Click: url-monitor service
3. Click: Environment tab
4. Click: Add Environment Variable
5. Set:
   Key:   ALLOWED_HOSTS
   Value: url-monitor-2xlk.onrender.com
6. Click: Save Changes
7. Wait: 2-3 minutes for automatic redeploy
8. Test: https://url-monitor-2xlk.onrender.com

⚠️  IMPORTANT: No https://, no www., just the domain!
""")
    else:
        print("\n✅ Configuration looks good!")
        print("   If still getting 400, try:")
        print("   1. Hard refresh browser (Ctrl+Shift+R)")
        print("   2. Clear browser cache")
        print("   3. Check for typos in environment variable")
    
    print("="*60 + "\n")

except ImportError as e:
    print(f"❌ Error importing Django: {e}")
    print("   Make sure you're running this in the correct environment")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
