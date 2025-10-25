# 🔧 Fix: Server Error 500 After Registration

## Problem
Getting a 500 Internal Server Error after successfully registering as a new user on Render.

## ⚠️ Important: Render Free Tier Limitations
**You CANNOT run commands via Shell on Render's free tier.** Migrations must happen during the build process automatically.

## Root Cause
The 500 error happens because database migrations didn't run successfully during deployment, usually because:

1. **PostgreSQL wasn't ready** when migrations tried to run during first build
2. **Build completed but migrations failed silently**
3. **Database tables don't exist** when the app tries to query them

---

## ✅ Solution: Trigger a Manual Redeploy

### Step 1: Check Current Deployment Status

1. Go to: **https://dashboard.render.com**
2. Click: **"url-monitor"** service
3. Click: **"Events"** tab
4. Look at the latest deploy - check if it says:
   - ✅ "Deploy succeeded" 
   - ❌ "Deploy failed"

### Step 2: Check Build Logs

1. In Events tab, click on the latest deployment
2. Look for migration messages in build logs:
   ```
   → Running database migrations...
   ✅ Migrations check passed, running migrations...
   Operations to perform:
     Apply all migrations: admin, auth, contenttypes, sessions, monitor
   Running migrations:
     Applying monitor.0001_initial... OK
     Applying monitor.0002_... OK
   ```

### Step 3: Trigger Manual Redeploy

If migrations didn't run or database wasn't ready:

1. Go to: **https://dashboard.render.com**
2. Click: **"url-monitor"** service  
3. Click: **"Manual Deploy"** button (top right)
4. Select: **"Clear build cache & deploy"**
5. Wait for deployment to complete (5-10 minutes)

This will:
- Rebuild from scratch
- Database will be ready this time
- Migrations will run successfully
- App should work after

---

## 🔍 Check If Database is Ready

### Verify PostgreSQL Service

1. In Render Dashboard, check if you have:
   - ✅ **url-monitor-db** (PostgreSQL) - should show "Available"
   - ✅ **url-monitor-redis** (Redis) - should show "Available"
   - ✅ **url-monitor** (Web Service) - should show "Live"

2. If database shows "Creating..." or "Unavailable":
   - Wait for it to finish provisioning
   - Then trigger manual redeploy of web service

---

## 🐛 Common Deployment Issues

### Issue 1: First Deploy Failed
**Symptom:** Database wasn't ready when web service built  
**Fix:** 
1. Wait for all services to show "Available" or "Live"
2. Trigger manual redeploy with "Clear build cache"

### Issue 2: Environment Variable Missing
**Symptom:** `ALLOWED_HOSTS` not set (causing 400 before you can even see 500)  
**Fix:**
1. Go to Environment tab
2. Add: `ALLOWED_HOSTS=url-monitor-2xlk.onrender.com`
3. Service will auto-redeploy

### Issue 3: Build Succeeded but Migrations Skipped
**Symptom:** Build logs don't show migration output  
**Fix:**
1. Check `build.sh` is executable
2. Verify `DATABASE_URL` is linked in render.yaml
3. Trigger manual redeploy

---

## 📋 Verify Migrations Ran Successfully

Check the build logs for these messages:

```
✅ GOOD - Migrations ran successfully:
→ Running database migrations...
✅ Migrations check passed, running migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, monitor
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying monitor.0001_initial... OK
  Applying monitor.0002_engagement_trafficmetric_userflow... OK
  Applying monitor.0003_pageview_clickheatmap_scrollheatmap... OK
  Applying monitor.0004_monitoredurl_group_and_more... OK
  Applying monitor.0005_pageview_engagement_and_more... OK
```

```
❌ BAD - Migrations failed:
⚠️  Migrations failed - this is expected on first deploy
→ Database not ready, will retry on next deploy
```

If you see the BAD message, **trigger a manual redeploy**.

---

## 🚀 Complete Fix Process

### 1. Ensure All Services are Ready
- PostgreSQL: "Available" ✅
- Redis: "Available" ✅  
- Web Service: Wait for it to finish building

### 2. Verify Environment Variables
Go to Environment tab and check:
- ✅ `ALLOWED_HOSTS=url-monitor-2xlk.onrender.com`
- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` (auto-generated)
- ✅ `DATABASE_URL` (auto-linked from database)
- ✅ `REDIS_URL` (auto-linked from Redis)

### 3. Trigger Redeploy
1. Click **"Manual Deploy"**
2. Select **"Clear build cache & deploy"**
3. Watch build logs for migration messages
4. Wait for "Deploy succeeded"

### 4. Test Registration
1. Go to: `https://url-monitor-2xlk.onrender.com/register/`
2. Create a new account
3. Should redirect to dashboard (empty, no URLs yet)
4. No 500 error!

---

## 🔧 Alternative: Check Actual Error

If you want to see the specific error:

### Temporarily Enable Debug Mode

1. Go to Environment tab in Render
2. Find `DEBUG` variable
3. Change value to: `True`
4. Wait for auto-redeploy
5. Try registering again
6. You'll see full error traceback instead of 500 page
7. **IMPORTANT:** Change `DEBUG` back to `False` after!

### Check Logs for Error

1. Go to **"Logs"** tab
2. Try registering/logging in again
3. Look for Python traceback in logs:
   ```python
   Traceback (most recent call last):
     File "/app/monitor/views.py", line 70, in dashboard
       urls = MonitoredURL.objects.filter(...)
   OperationalError: relation "monitor_monitoredurl" does not exist
   ```

This tells you exactly what's wrong!

---

## 📦 Deployment Order Matters

Render provisions services in this order:
1. **PostgreSQL** (2-3 minutes)
2. **Redis** (1-2 minutes)  
3. **Web Service** builds (5-10 minutes)
   - If DB not ready → migrations fail
   - Need to redeploy after DB is ready

**Solution:** If first deploy shows migration errors, just redeploy after all services are up.

---

## 🎯 Quick Troubleshooting Checklist

- [ ] PostgreSQL service shows "Available"
- [ ] Redis service shows "Available"
- [ ] `ALLOWED_HOSTS` environment variable is set
- [ ] Latest deploy shows "Deploy succeeded" (not failed)
- [ ] Build logs show migrations ran successfully
- [ ] Can access login page without 400 error
- [ ] Registration creates user but 500 on redirect

If all checked except last one: **Trigger manual redeploy with cache clear**

---

## 🐛 Still Not Working?

### Get Detailed Error Information

1. **Enable DEBUG temporarily:**
   - Environment → DEBUG=True
   - Wait for redeploy
   - Try registration
   - See full error page
   - Set DEBUG=False after

2. **Check Logs for specific error:**
   - Logs tab → Look for traceback
   - Common errors:
     - `relation "monitor_monitoredurl" does not exist` → Needs redeploy
     - `no such table` → Needs redeploy
     - `SMTP` error → Email config issue (non-critical)
     - `Redis` error → Redis not connected

3. **Verify Database Connection:**
   - Check DATABASE_URL is set in environment
   - Should start with `postgres://` or `postgresql://`
   - Should be auto-linked from url-monitor-db

---

## ✅ Success Indicators

After successful fix:
- Registration works without error
- Redirect to dashboard succeeds
- Dashboard shows empty state (no URLs monitored yet)
- Can navigate to "Add URL" page
- Can create alerts, view notifications

---

## 🔄 Force Fresh Deployment

If nothing works, try completely fresh deployment:

1. **Delete and Recreate:**
   - In Render, delete web service (keep database!)
   - Push code to GitHub
   - Create new web service from Blueprint
   - Link to existing database

2. **Or Clear Everything:**
   - Manual Deploy → Clear build cache & deploy
   - This forces complete rebuild

---

## 📝 Prevention Tips

### For Future Deployments:

1. **Always wait for DB to provision** before web service builds
2. **Check build logs** for migration success messages
3. **Set ALLOWED_HOSTS** immediately after first deploy
4. **Trigger redeploy** if first build was before DB was ready

### Your build.sh is Correct:
```bash
#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate  # ← This runs during build
```

---

## 🆘 Need More Help?

Share this information:
1. Build logs (Events → Latest deploy → View logs)
2. Error from Logs tab (Python traceback)
3. Screenshot of Services dashboard (all service statuses)

---

**MOST LIKELY FIX:** 
1. Wait for PostgreSQL to show "Available"
2. Click "Manual Deploy" → "Clear build cache & deploy"
3. Wait 5-10 minutes
4. Try registration again

**STATUS:** Your build.sh is correct. The issue is timing - database wasn't ready during first build.

```bash
#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate  # ← This line is important!
```

If missing, add it and redeploy.

---

## Debug in Render Shell

Run this diagnostic script:

```python
# In Render Shell, run Python
python manage.py shell

# Then run these commands:
from django.contrib.auth.models import User
from monitor.models import MonitoredURL

# Check if users exist
print(f"Total users: {User.objects.count()}")

# Check if tables exist
try:
    print(f"Total URLs: {MonitoredURL.objects.count()}")
    print("✅ Database tables exist")
except Exception as e:
    print(f"❌ Error: {e}")
    print("→ Run: python manage.py migrate")
```

---

## Common Error Messages & Fixes

### "relation 'monitor_monitoredurl' does not exist"
**Fix:** Run `python manage.py migrate`

### "SMTP AUTH extension not supported"
**Fix:** Check `EMAIL_HOST` and credentials in environment variables

### "OperationalError: no such table"
**Fix:** Run `python manage.py migrate`

### "ProgrammingError: relation does not exist"
**Fix:** Run `python manage.py migrate --run-syncdb`

---

## Prevention for Future Deployments

Make sure `build.sh` always runs migrations:

```bash
#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations (IMPORTANT!)
python manage.py migrate

# Optional: Create default data
# python manage.py loaddata initial_data.json
```

---

## Test After Fix

1. **Test Registration:**
   - Go to: `https://url-monitor-2xlk.onrender.com/register/`
   - Create a new account
   - Should redirect to dashboard without error

2. **Test Dashboard:**
   - Should show empty dashboard (no URLs monitored yet)
   - No 500 error

3. **Test Adding URL:**
   - Click "Add URL"
   - Add a test URL
   - Should save successfully

---

## Get Detailed Error Info

If still getting 500 error, check Render logs:

1. Go to Render Dashboard → Logs tab
2. Look for Python traceback (usually shows after 500 error)
3. Post the traceback here for specific help

Example of what to look for:
```
Traceback (most recent call last):
  File "/app/monitor/views.py", line 70, in dashboard
    urls = MonitoredURL.objects.filter(...)
  ...
OperationalError: no such table: monitor_monitoredurl
```

This will tell us exactly what's wrong!

---

**Most Likely Fix:** Run `python manage.py migrate` in Render Shell

**Second Most Likely:** Check `build.sh` includes migrations

**Third:** Check actual error in Render logs
