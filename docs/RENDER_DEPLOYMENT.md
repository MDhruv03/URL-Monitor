# Render Deployment Guide for URL Monitor

## Prerequisites

1. **Render Account**: Sign up at https://render.com (free tier available)
2. **GitHub Repository**: Push your URL Monitor code to GitHub
3. **Environment Ready**: All files updated with production configurations

## Quick Deploy (Blueprint Method)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Deploy on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the repository containing `render.yaml`
5. Click **"Apply"**

Render will automatically:
- Create a PostgreSQL database
- Create a Redis instance
- Deploy your web service
- Set up environment variables

### Step 3: Set Environment Variables

In Render Dashboard → Web Service → Environment:

**Required:**
```
SECRET_KEY=<generate-a-random-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=<automatically-set-by-render>
REDIS_URL=<automatically-set-by-render>
```

**Optional (for full features):**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
SLACK_WEBHOOK_URL=your-slack-webhook
```

## Manual Deploy (Without Blueprint)

If you prefer manual setup or Blueprint doesn't work:

### Step 1: Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `url-monitor-db`
3. Database Name: `url_monitor`
4. Plan: **Free**
5. Click **"Create Database"**
6. Copy the **Internal Database URL** (starts with `postgres://`)

### Step 2: Create Redis Instance

1. Click **"New +"** → **"Redis"**
2. Name: `url-monitor-redis`
3. Plan: **Free**
4. Click **"Create Redis"**
5. Copy the **Internal Redis URL** (starts with `redis://`)

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `url-monitor`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn url_monitor.wsgi:application`
   - **Plan**: **Free**

### Step 4: Set Environment Variables

Add these in the Environment section:

```bash
# Django Settings
SECRET_KEY=django-insecure-change-this-to-a-random-50-char-string
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com

# Database (paste from Step 1)
DATABASE_URL=postgres://user:password@hostname:5432/url_monitor

# Redis (paste from Step 2)
REDIS_URL=redis://hostname:6379

# Celery
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Deploy

Click **"Create Web Service"**. Render will:
1. Pull your code from GitHub
2. Run `build.sh` (install dependencies, collect static files, migrate database)
3. Start the application with Gunicorn

## Post-Deployment

### Create Superuser

Once deployed, use Render's Shell feature:

1. Go to your Web Service → **Shell** tab
2. Run:
```bash
python manage.py createsuperuser
```

### Access Your App

Your app will be available at:
```
https://your-app-name.onrender.com
```

Admin panel:
```
https://your-app-name.onrender.com/admin/
```

### Set Up Celery Worker (Optional but Recommended)

For background tasks (URL checking):

1. Click **"New +"** → **"Background Worker"**
2. Connect same repository
3. Configure:
   - **Name**: `url-monitor-worker`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A url_monitor worker --loglevel=info`
4. Add same environment variables as web service
5. Click **"Create Background Worker"**

### Set Up Celery Beat (Optional but Recommended)

For scheduled URL checks:

1. Click **"New +"** → **"Background Worker"**
2. Connect same repository
3. Configure:
   - **Name**: `url-monitor-beat`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A url_monitor beat --loglevel=info`
4. Add same environment variables as web service
5. Click **"Create Background Worker"**

## Troubleshooting

### Build Fails with "pip install" Error

**Problem**: Package installation fails

**Solutions**:
1. Check `requirements.txt` for typos or incompatible versions
2. Ensure Python version matches (3.11)
3. Add `--no-cache-dir` to pip commands in `build.sh`:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

### Static Files Not Loading

**Problem**: CSS/JS not loading, plain HTML only

**Solutions**:
1. Verify `build.sh` runs `collectstatic`:
   ```bash
   python manage.py collectstatic --no-input
   ```
2. Check `STATIC_ROOT` in settings.py:
   ```python
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   ```
3. Verify WhiteNoise is in `MIDDLEWARE` (should be second)

### Database Connection Error

**Problem**: `OperationalError: could not connect to server`

**Solutions**:
1. Verify `DATABASE_URL` environment variable is set
2. Use **Internal Database URL** from Render (not External)
3. Check database service is running in Render dashboard

### ALLOWED_HOSTS Error

**Problem**: `DisallowedHost at /`

**Solutions**:
1. Add your Render domain to `ALLOWED_HOSTS`:
   ```bash
   ALLOWED_HOSTS=your-app-name.onrender.com,.onrender.com
   ```
2. In settings.py, ensure it reads from environment:
   ```python
   ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
   ```

### Redis Connection Error

**Problem**: Celery can't connect to Redis

**Solutions**:
1. Verify `REDIS_URL` environment variable
2. Use **Internal Redis URL** from Render
3. Ensure Redis service is running

### Build Takes Too Long / Times Out

**Problem**: Build exceeds 15 minutes (free tier limit)

**Solutions**:
1. Remove unnecessary packages from `requirements.txt`
2. Use `--no-cache-dir` in pip install
3. Consider upgrading to paid tier for longer build times

## Updating Your Deployment

### Method 1: Auto-Deploy (Recommended)

Render auto-deploys when you push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will automatically rebuild and deploy.

### Method 2: Manual Deploy

In Render Dashboard:
1. Go to your Web Service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

## Monitoring

### View Logs

Render Dashboard → Web Service → **Logs** tab

Shows:
- Application logs
- Build logs
- Error messages

### Check Service Status

Dashboard shows:
- ✅ Running
- 🔄 Building
- ❌ Failed

### Database Access

Render Dashboard → PostgreSQL → **Connect**

Use provided credentials to connect via:
- `psql` command line
- GUI tools (pgAdmin, DBeaver)
- Direct SQL queries

## Performance Tips

### Free Tier Limitations

Render Free tier has:
- ⏰ Services spin down after 15 minutes of inactivity
- ⏳ ~30 second cold start time
- 💾 750 hours/month (shared across all services)

### Keep Service Awake

Use a service like **UptimeRobot** or **Pingdom** to ping your app every 14 minutes.

Or create a simple cron job:
```bash
# Ping every 10 minutes
*/10 * * * * curl https://your-app-name.onrender.com
```

### Optimize for Speed

1. **Enable compression**:
   ```python
   # settings.py
   MIDDLEWARE = [
       'django.middleware.gzip.GZipMiddleware',  # Add this
       # ... rest
   ]
   ```

2. **Use caching**:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': config('REDIS_URL'),
       }
   }
   ```

## Security Checklist

Before going to production:

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` (50+ random characters)
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Use environment variables for secrets (never commit to Git)
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up proper CORS headers for external tracking
- [ ] Configure secure cookies:
  ```python
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  ```

## Cost Estimate

**Free Tier** (What you get for $0/month):
- ✅ Web Service (750 hours/month)
- ✅ PostgreSQL Database (90 days, then expires)
- ✅ Redis Instance (25 MB storage)
- ✅ SSL Certificate
- ✅ Auto-deploys from Git
- ⚠️ Services sleep after inactivity
- ⚠️ Database expires after 90 days

**Paid Starter** ($7/month per service):
- ✅ Always-on (no sleeping)
- ✅ Persistent PostgreSQL
- ✅ More resources
- ✅ Custom domains

## Support

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/5.2/howto/deployment/
- **Community**: https://community.render.com

## Next Steps

After successful deployment:

1. ✅ Test all features in production
2. ✅ Update tracking script URLs on monitored sites
3. ✅ Set up monitoring alerts
4. ✅ Configure backup strategy
5. ✅ Add custom domain (optional)
6. ✅ Set up CI/CD (GitHub Actions)

## Quick Reference

### Important URLs
- Dashboard: https://dashboard.render.com
- Your App: https://your-app-name.onrender.com
- Admin: https://your-app-name.onrender.com/admin

### Essential Commands
```bash
# Local testing
python manage.py runserver

# Check for issues
python manage.py check --deploy

# Create superuser (in Render Shell)
python manage.py createsuperuser

# Run migrations (in Render Shell)
python manage.py migrate

# Collect static files (in build.sh)
python manage.py collectstatic --no-input
```

---

🎉 **You're ready to deploy!** Follow the steps above and your URL Monitor will be live on the internet.
