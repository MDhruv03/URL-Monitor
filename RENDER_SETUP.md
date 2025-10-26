# Render Deployment Setup Guide

## Current Status
Your app is deployed at: https://url-monitor-2xlk.onrender.com
Health check shows: **"celery_workers": "no workers available"**

This means:
- ✅ Django web app is running
- ✅ PostgreSQL database is connected
- ❌ Celery workers are NOT running
- ❌ Redis is NOT configured

## What You Need

To make URL monitoring work, you need **5 services**:

1. **Web Service** (Django) - ✅ Already running
2. **PostgreSQL Database** - ✅ Already connected
3. **Redis Instance** - ❌ Missing (Required for Celery)
4. **Celery Worker** - ❌ Missing (Checks URLs)
5. **Celery Beat** - ❌ Missing (Schedules checks)

## Quick Setup: Use Blueprint (Recommended)

Your `render.yaml` file already defines everything. Just deploy it:

### Steps:

1. **Go to Render Dashboard**
   - https://dashboard.render.com

2. **Delete Current Manual Deployment** (Optional but cleaner)
   - If you want a fresh start, delete `url-monitor-2xlk`
   - Keep the database if it has data you want

3. **Create Blueprint Instance**
   - Click **"New +"** at top
   - Select **"Blueprint"**
   - Click **"Connect a repository"**
   - Choose **"MDhruv03/URL-Monitor"**
   - Render detects `render.yaml` automatically
   - Click **"Apply"**

4. **Blueprint Creates Everything**
   - Provisions all 5 services automatically
   - Configures environment variables
   - Connects services together
   - Takes ~5-10 minutes

5. **Verify Deployment**
   ```powershell
   curl https://YOUR-NEW-URL.onrender.com/health/
   ```
   Should show: `"celery_workers": "running (1 workers)"`

## Manual Setup: Add Missing Services

If you want to keep your current web service:

### 1. Create Redis

- Dashboard → **New +** → **Redis**
- **Name**: `url-monitor-redis`
- **Region**: Same as your web service
- **Plan**: Free
- **Create Redis**
- After created, go to **"Connect"** tab
- Copy **"Internal Redis URL"** (format: `redis://red-xxxxx:6379`)

### 2. Update Web Service Environment Variables

- Go to your web service (`url-monitor-2xlk`)
- **Environment** tab
- Add/Update these variables:
  ```
  REDIS_URL = redis://red-xxxxx:6379  (from step 1)
  CELERY_BROKER_URL = redis://red-xxxxx:6379  (same as REDIS_URL)
  ```
- Click **"Save Changes"** (will trigger redeploy)

### 3. Create Celery Worker

- Dashboard → **New +** → **Background Worker**
- **Name**: `url-monitor-worker`
- **Environment**: Python 3
- **Region**: Same as web service
- **Repository**: MDhruv03/URL-Monitor
- **Branch**: main
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `celery -A url_monitor worker --loglevel=info`

**Environment Variables** (click "Add Environment Variable" for each):
```
DATABASE_URL = [Copy from web service]
SECRET_KEY = [Copy from web service]
REDIS_URL = redis://red-xxxxx:6379
CELERY_BROKER_URL = redis://red-xxxxx:6379
DEBUG = False
ALLOWED_HOSTS = *
```

- Click **"Create Background Worker"**

### 4. Create Celery Beat

- Dashboard → **New +** → **Background Worker**
- **Name**: `url-monitor-beat`
- **Environment**: Python 3
- **Region**: Same as web service
- **Repository**: MDhruv03/URL-Monitor
- **Branch**: main
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `celery -A url_monitor beat --loglevel=info`

**Environment Variables** (same as worker):
```
DATABASE_URL = [Copy from web service]
SECRET_KEY = [Copy from web service]
REDIS_URL = redis://red-xxxxx:6379
CELERY_BROKER_URL = redis://red-xxxxx:6379
DEBUG = False
```

- Click **"Create Background Worker"**

### 5. Verify Everything Works

Wait 2-3 minutes for services to start, then:

```powershell
# Check health
curl https://url-monitor-2xlk.onrender.com/health/

# Should return:
{
  "status": "healthy",
  "database": "connected",
  "celery_workers": "running (1 workers)",  ← This should say "running"
  "tables": {"users": 3, "monitored_urls": 3},
  "migrations": "applied"
}
```

**Test URL Monitoring:**
1. Go to https://url-monitor-2xlk.onrender.com/urls/
2. Click "Check Now" on any URL
3. Should update status within seconds

**Check Logs:**
```
Dashboard → url-monitor-worker → Logs tab
```
Should see:
```
[tasks]
  . monitor.tasks.check_url_status
  . monitor.tasks.schedule_checks
  . monitor.tasks.send_alert

celery@worker ready.
```

## Troubleshooting

### Health check still shows "no workers available"

**Check worker logs:**
- Dashboard → url-monitor-worker → Logs
- Look for errors connecting to Redis or database

**Verify Redis URL:**
- Make sure all 3 services (web, worker, beat) have the **same** Redis URL
- URL should be the **Internal** connection string (starts with `redis://red-`)

### Worker can't connect to Redis

**Error**: `Error: Error 111 connecting to redis`

**Solution**: 
- Redis instance must be in same region as workers
- Use Internal connection string, not External
- Format: `redis://red-xxxxx:6379` (no password for internal)

### Worker can't import tasks

**Error**: `Unable to load celery configuration`

**Solution**:
- Make sure worker has `DATABASE_URL` environment variable
- Check build logs show `pip install -r requirements.txt` succeeded

### Beat schedule conflicts

**Error**: `DatabaseError: already exists`

**Solution**:
- Only run **ONE** beat instance
- Beat stores schedule in database
- Multiple beats will conflict

## Cost Summary (Free Tier)

All services can run on Render's free tier:
- Web Service: Free ($0/month)
- Background Worker (Celery): Free ($0/month)
- Background Worker (Beat): Free ($0/month)
- PostgreSQL: Free ($0/month)
- Redis: Free ($0/month)

**Total: $0/month** ✅

Note: Free tier services:
- Sleep after 15 minutes of inactivity
- Have 750 hours/month limit per service
- Redis limited to 25MB memory

For production with 24/7 uptime, upgrade to paid plans ($7-25/month per service).

## Quick Commands

**Check all services:**
```powershell
# Health check
curl https://url-monitor-2xlk.onrender.com/health/

# Get detailed JSON
curl https://url-monitor-2xlk.onrender.com/health/ | ConvertFrom-Json | ConvertTo-Json

# Run local diagnostics
python manage.py check_celery
```

**Monitor logs in real-time:**
- Dashboard → Click service → Logs tab → Enable "Live Logs"

## Next Steps After Setup

Once workers are running:

1. **Configure Alert Integrations**
   - Settings → Add email/Telegram/Slack webhooks
   - Test alerts work

2. **Add URLs to Monitor**
   - Dashboard → Add URLs
   - Set check frequency (1-60 minutes)
   - Set expected status codes

3. **Monitor Dashboard**
   - Check status indicators
   - View response time graphs
   - Review alert history

4. **Set Up Notifications**
   - Email alerts for downtime
   - Telegram/Slack webhooks
   - SMS via Twilio (optional)
