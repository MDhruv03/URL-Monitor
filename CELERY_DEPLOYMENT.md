# Celery Deployment Guide

## Why Celery is Required

This URL monitoring application uses **Celery** for asynchronous task execution. Celery workers are essential for:

- **URL Status Checks**: Periodically checking if monitored URLs are up or down
- **Alert Notifications**: Sending email/Telegram/Slack alerts when URLs go down
- **Scheduled Tasks**: Running automated checks based on configured frequencies

**Without Celery workers running, URL status checks will not happen automatically.**

## Quick Diagnosis

Check if Celery is running:

```bash
python manage.py check_celery
```

Or check via the health endpoint:
```
GET /health/
```

Response includes `celery_workers` status.

## Local Development

### 1. Start Redis (Required for Celery)

**Option A: Docker**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Option B: Windows**
```powershell
# Download Redis for Windows from GitHub
# Or use WSL: sudo service redis-server start
```

**Option C: macOS/Linux**
```bash
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu/Debian
redis-server
```

### 2. Start Celery Worker

In a **separate terminal**:
```bash
celery -A url_monitor worker --loglevel=info
```

### 3. Start Celery Beat (for scheduled checks)

In **another separate terminal**:
```bash
celery -A url_monitor beat --loglevel=info
```

### 4. Start Django Development Server

```bash
python manage.py runserver
```

You should now have **3 processes running**:
1. Django server (port 8000)
2. Celery worker (background tasks)
3. Celery beat (scheduler)

## Production Deployment

### Option 1: Using Supervisor (Recommended)

Create `/etc/supervisor/conf.d/url_monitor.conf`:

```ini
[program:url_monitor_celery]
command=/path/to/venv/bin/celery -A url_monitor worker --loglevel=info
directory=/path/to/url_monitor
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.err.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600

[program:url_monitor_celery_beat]
command=/path/to/venv/bin/celery -A url_monitor beat --loglevel=info
directory=/path/to/url_monitor
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.err.log
autostart=true
autorestart=true
startsecs=10
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start url_monitor_celery url_monitor_celery_beat
```

### Option 2: Using Systemd

Create `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker for URL Monitor
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/url_monitor
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A url_monitor worker --loglevel=info --detach
ExecStop=/path/to/venv/bin/celery -A url_monitor control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/celery-beat.service`:

```ini
[Unit]
Description=Celery Beat for URL Monitor
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/url_monitor
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A url_monitor beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
sudo systemctl status celery-worker celery-beat
```

### Option 3: Docker Compose

Add to your `docker-compose.yml`:

```yaml
services:
  web:
    build: .
    command: gunicorn url_monitor.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  celery-worker:
    build: .
    command: celery -A url_monitor worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  celery-beat:
    build: .
    command: celery -A url_monitor beat --loglevel=info
    volumes:
      - .:/app
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

Start all services:
```bash
docker-compose up -d
```

### Option 4: Platform-Specific (Heroku, Railway, etc.)

**Heroku:**
Add to `Procfile`:
```
web: gunicorn url_monitor.wsgi
worker: celery -A url_monitor worker --loglevel=info
beat: celery -A url_monitor beat --loglevel=info
```

Then scale workers:
```bash
heroku ps:scale worker=1 beat=1
```

**Railway/Render:**
Create separate services for:
1. Web (Django)
2. Worker (Celery worker)
3. Beat (Celery beat)

All pointing to same codebase with different start commands.

## Environment Variables

Ensure these are set:

```bash
# Redis connection for Celery
CELERY_BROKER_URL=redis://localhost:6379/0
# or for Upstash Redis:
CELERY_BROKER_URL=rediss://default:password@host:port

# Optional: Result backend (can be None)
CELERY_RESULT_BACKEND=None
```

## Troubleshooting

### Workers not connecting to Redis

**Check Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**Check connection string:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)
```

### Tasks not executing

**Check worker is receiving tasks:**
```bash
celery -A url_monitor inspect active
```

**Check task registration:**
```bash
celery -A url_monitor inspect registered
```

### Manual URL Check

If Celery isn't working, you can manually check URLs:

```bash
python manage.py check_celery
```

Or in Django admin, click "Check Now" on any URL (now has automatic fallback to synchronous execution).

## Monitoring

**Check worker stats:**
```bash
celery -A url_monitor inspect stats
```

**Check active tasks:**
```bash
celery -A url_monitor inspect active
```

**Check scheduled tasks:**
```bash
celery -A url_monitor inspect scheduled
```

**Flower (Web UI for Celery):**
```bash
pip install flower
celery -A url_monitor flower
# Access at http://localhost:5555
```

## Performance Tuning

For production with many URLs:

```bash
# Multiple workers with concurrency
celery -A url_monitor worker --concurrency=4 --loglevel=info

# Separate queues for different priorities
celery -A url_monitor worker -Q high_priority,default --loglevel=info
```

## Security Notes

- Always use SSL/TLS for Redis in production (rediss://)
- Restrict Redis network access to application servers only
- Use strong passwords for Redis authentication
- Monitor worker logs for security issues

## Need Help?

- Check logs: `/var/log/celery/` or `docker logs <container>`
- Run diagnostics: `python manage.py check_celery`
- Check health: `curl https://your-domain.com/health/`
