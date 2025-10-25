# Celery Setup for URL Monitoring

## Issue: Check Button Not Working

The "Check Now" button requires Celery workers to be running to process URL checks in the background.

## Local Development Setup

### 1. Start Redis (Required for Celery)
Celery uses Redis as a message broker. Make sure Redis is running:

**If using local Redis:**
```bash
redis-server
```

**If using Upstash Redis (already configured):**
Your `.env` file already has Upstash Redis configured - no additional setup needed.

### 2. Start Celery Worker
Open a **new terminal** and run:

```bash
cd c:\Users\Dhruv\Desktop\WORK\PROJECTS\url_monitor
celery -A url_monitor worker --loglevel=info --pool=solo
```

**Note:** Use `--pool=solo` on Windows as eventlet/gevent don't work well on Windows.

### 3. Start Celery Beat (Optional - for automatic checks)
Open **another terminal** and run:

```bash
cd c:\Users\Dhruv\Desktop\WORK\PROJECTS\url_monitor
celery -A url_monitor beat --loglevel=info
```

### 4. Start Django Development Server
```bash
python manage.py runserver
```

## Production Setup (Render.com)

Your `render.yaml` should have these services:

```yaml
services:
  # Web Service
  - type: web
    name: url-monitor
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn url_monitor.wsgi:application
    
  # Celery Worker
  - type: worker
    name: url-monitor-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A url_monitor worker --loglevel=info
    
  # Celery Beat (for scheduled tasks)
  - type: worker
    name: url-monitor-beat
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A url_monitor beat --loglevel=info
```

## Testing the Check Button

1. Make sure Celery worker is running
2. Go to URL Monitor dashboard
3. Click "Check Now" on any URL
4. You should see:
   - Button shows "Checking..." briefly
   - Status updates after a few seconds
   - Check logs in Celery worker terminal

## Troubleshooting

### Check Button does nothing:
- **Cause:** Celery worker not running
- **Solution:** Start Celery worker (see step 2 above)

### Error: "Connection refused localhost:6379"
- **Cause:** Redis not running or wrong Redis URL
- **Solution:** 
  - Check `.env` file has correct `CELERY_BROKER_URL`
  - For Upstash: `rediss://default:YOUR_TOKEN@central-monkey-22361.upstash.io:6379`
  - Make sure SSL settings are configured in `settings.py`

### Worker starts but crashes:
- **Cause:** Database connection issues or missing dependencies
- **Solution:** 
  - Check `DATABASE_URL` in `.env`
  - Run `pip install -r requirements.txt`

## Current Configuration

Your project is already configured with:
- ✅ Upstash Redis (cloud Redis service)
- ✅ SSL configuration for secure Redis connection
- ✅ Celery tasks defined in `monitor/tasks.py`
- ✅ Periodic task to check URLs every minute

**You just need to start the Celery worker!**
