# 🔧 Fix: 400 Bad Request Error on Render

## Problem
Your service deployed successfully but returns **400 Bad Request** when accessing `https://url-monitor-2xlk.onrender.com`

## Root Cause
Django's `ALLOWED_HOSTS` setting doesn't include your Render domain.

## ⚠️ CRITICAL: Port Issue Detected
Your logs show:
```
Detected a new open port HTTP:8000
Shutting down: Master
```

This means the Dockerfile is still using hardcoded port 8000. **The fix from v2.0.1 needs to be deployed!**

---

## Quick Fix (Set Environment Variable in Render)

### Step 1: Go to Render Dashboard
1. Visit https://dashboard.render.com
2. Click on your `url-monitor` service
3. Go to **Environment** tab

### Step 2: Add/Update ALLOWED_HOSTS
Click **Add Environment Variable** and set:

```
Key:   ALLOWED_HOSTS
Value: url-monitor-2xlk.onrender.com,localhost,127.0.0.1
```

> **Important**: Don't include `https://` in ALLOWED_HOSTS. Just the domain!

### Step 3: Redeploy
After adding the environment variable, Render will automatically redeploy your service.

---

## Alternative: Update .env File (For Future Deployments)

If you want to set this in your code (less recommended for production):

```bash
# .env file
ALLOWED_HOSTS=url-monitor-2xlk.onrender.com,localhost,127.0.0.1
```

Then commit and push to trigger a redeploy.

---

## ⚠️ SECOND ISSUE: Port Binding

Your logs show the service is **still using port 8000** instead of Render's dynamic `$PORT`.

### Verify Dockerfile Fix
Check that your `Dockerfile` has this line (from v2.0.1 fix):

```dockerfile
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 url_monitor.wsgi:application
```

**NOT** this (old version):
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", ...]
```

### If Dockerfile is Correct
1. **Commit the changes**:
   ```bash
   git add Dockerfile
   git commit -m "Fix: Use dynamic PORT for Render"
   git push origin main
   ```

2. **Trigger Manual Deploy** in Render dashboard if auto-deploy doesn't work

---

## Complete Solution (Both Fixes)

### 1. Set ALLOWED_HOSTS in Render
```
ALLOWED_HOSTS=url-monitor-2xlk.onrender.com
```

### 2. Verify Dockerfile Uses Dynamic Port
```dockerfile
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 url_monitor.wsgi:application
```

### 3. Verify render.yaml Uses $PORT
```yaml
startCommand: "gunicorn url_monitor.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120"
```

### 4. Push Changes and Redeploy
```bash
git add .
git commit -m "Fix: ALLOWED_HOSTS and port binding"
git push origin main
```

---

## Verification

After deploying, you should see in logs:

✅ **Correct:**
```
Listening at: http://0.0.0.0:10000  (or any port != 8000)
```

❌ **Wrong:**
```
Listening at: http://0.0.0.0:8000
Detected a new open port HTTP:8000
Shutting down: Master
```

---

## Test Your Service

Once deployed with both fixes:

### 1. Test Homepage
```bash
curl https://url-monitor-2xlk.onrender.com/
```
Should return HTML (not 400 error)

### 2. Test Admin Panel
```bash
https://url-monitor-2xlk.onrender.com/admin/
```
Should show Django admin login

### 3. Test Tracking Script
```bash
curl https://url-monitor-2xlk.onrender.com/tracking/1/script.js
```
Should return JavaScript code

---

## Common Issues After Fix

### Still Getting 400?
- Check ALLOWED_HOSTS is set correctly (no typos)
- Check you included the domain without `https://`
- Verify service redeployed after setting env var

### Service Still Restarting?
- Verify Dockerfile uses `${PORT:-8000}`
- Check render.yaml uses `$PORT`
- Look for hardcoded `8000` anywhere in start commands

### Static Files Not Loading?
- Run `python manage.py collectstatic --noinput` in Render shell
- Verify `build.sh` includes collectstatic command

---

## Environment Variables Checklist

Make sure these are set in Render:

### Required
- ✅ `SECRET_KEY` (auto-generated)
- ✅ `DEBUG=False`
- ✅ `ALLOWED_HOSTS=url-monitor-2xlk.onrender.com`
- ✅ `DATABASE_URL` (auto-linked)
- ✅ `REDIS_URL` (auto-linked)
- ✅ `CELERY_BROKER_URL` (same as REDIS_URL)
- ✅ `CELERY_RESULT_BACKEND` (same as REDIS_URL)

### Optional
- `EMAIL_HOST=smtp.gmail.com`
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_HOST_USER=your-email@gmail.com`
- `EMAIL_HOST_PASSWORD=your-app-password`
- `TELEGRAM_BOT_TOKEN=...`
- `SLACK_WEBHOOK_URL=...`

---

## Quick Commands for Render Shell

```bash
# Check Django settings
python manage.py diffsettings

# Check ALLOWED_HOSTS
python -c "from django.conf import settings; print(settings.ALLOWED_HOSTS)"

# Test database connection
python manage.py dbshell

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate
```

---

## Success Indicators

✅ **Everything Working When:**
- Homepage loads without 400 error
- Admin panel accessible
- Logs show: `Listening at: http://0.0.0.0:XXXXX` (dynamic port)
- No "Detected a new open port" messages
- No repeated restarts
- Service stays "Live" (green status)

---

## Get Help

If you're still having issues:

1. **Check Render Logs** - Look for specific error messages
2. **Verify Environment Variables** - Double-check all values
3. **Check GitHub Commit** - Ensure latest code is pushed
4. **Review Documentation**:
   - [RENDER_TROUBLESHOOTING.md](RENDER_TROUBLESHOOTING.md)
   - [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

---

**Last Updated:** October 25, 2025  
**Your Service URL:** https://url-monitor-2xlk.onrender.com  
**Status:** Awaiting ALLOWED_HOSTS fix
