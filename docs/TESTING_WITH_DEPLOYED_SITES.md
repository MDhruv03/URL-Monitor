# Testing External Tracking with Deployed Sites

## The Problem

When you embed the tracking script on a deployed website (e.g., `https://dhruvm.netlify.app`), it tries to send data to your tracking endpoint. If your URL Monitor is running locally at `http://127.0.0.1:8000`, the deployed site **cannot reach it** because:

- `127.0.0.1` only exists on your local computer
- Your deployed site is on the internet and can't access `localhost`
- Even with CORS headers, it's physically impossible

## Solution 1: Use ngrok for Testing (Quick & Easy)

ngrok creates a secure tunnel to your localhost, giving you a public URL.

### Step 1: Install ngrok
1. Download from: https://ngrok.com/download
2. Extract and place `ngrok.exe` somewhere accessible
3. Sign up for free account at https://ngrok.com
4. Get your auth token from dashboard

### Step 2: Authenticate ngrok
```bash
ngrok authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 3: Start ngrok Tunnel
With your Django server running at `http://127.0.0.1:8000`:

```bash
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.0.0
Region                        United States (us)
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

### Step 4: Update Your Tracking Script URL
Instead of:
```html
<script src="http://127.0.0.1:8000/tracking/f6282f4d-b486-4ec3-97d1-a881789dfa3d/script.js"></script>
```

Use the ngrok URL:
```html
<script src="https://abc123.ngrok.io/tracking/f6282f4d-b486-4ec3-97d1-a881789dfa3d/script.js"></script>
```

### Step 5: Update Django ALLOWED_HOSTS
Add the ngrok domain to your settings:

```python
# url_monitor/settings.py
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'abc123.ngrok.io']
```

### Step 6: Test
1. Update the script tag on your Netlify site
2. Visit your site at `https://dhruvm.netlify.app`
3. Open DevTools → Network tab
4. You should see successful requests to `https://abc123.ngrok.io/api/track/...`

## Solution 2: Deploy URL Monitor (Production)

For production use, deploy your URL Monitor application to a public server.

### Deployment Options

#### Option A: Railway (Easiest - Free Tier Available)
1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Connect your URL-Monitor repository
4. Railway auto-detects Django and deploys
5. Get your public URL: `https://your-app.railway.app`

#### Option B: Heroku (Popular - Free Tier Ended)
1. Sign up at https://heroku.com
2. Install Heroku CLI
3. Create `Procfile`:
   ```
   web: gunicorn url_monitor.wsgi
   ```
4. Create `runtime.txt`:
   ```
   python-3.11.0
   ```
5. Deploy:
   ```bash
   heroku create your-url-monitor
   git push heroku main
   heroku run python manage.py migrate
   ```

#### Option C: DigitalOcean App Platform
1. Sign up at https://digitalocean.com
2. Create new App from GitHub repo
3. Configure build and run commands
4. Deploy

#### Option D: AWS Elastic Beanstalk
1. Sign up at https://aws.amazon.com
2. Install EB CLI
3. Initialize and deploy:
   ```bash
   eb init
   eb create
   eb deploy
   ```

### After Deployment

1. **Update ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   ```

2. **Update Tracking Script URL** on your monitored sites:
   ```html
   <script src="https://your-monitor.railway.app/tracking/{url_id}/script.js"></script>
   ```

3. **Configure Database**: Most platforms provide PostgreSQL
   ```python
   # settings.py
   import dj_database_url
   DATABASES['default'] = dj_database_url.config(conn_max_age=600)
   ```

4. **Set Environment Variables**:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `DATABASE_URL`

5. **Serve Static Files**: Use WhiteNoise
   ```bash
   pip install whitenoise
   ```
   
   ```python
   # settings.py
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
       # ... rest
   ]
   ```

## Solution 3: Local Testing with Same-Origin

If you just want to test locally without deployment:

1. **Download your Netlify site** and run it locally
2. **Use a local web server** (e.g., Python's HTTP server):
   ```bash
   python -m http.server 8080
   ```
3. **Open** `http://localhost:8080` in browser
4. **Update tracking script** to point to `http://127.0.0.1:8000`

This avoids CORS issues because both are on `localhost`.

## Checking if CORS is Working

Once you have a public URL (via ngrok or deployment), test CORS:

```bash
# Test preflight request
curl -X OPTIONS \
  -H "Origin: https://dhruvm.netlify.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  https://your-public-url.com/api/track/your-url-id/
```

Expected response headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## Troubleshooting

### CORS Error Still Appears
- ✅ Verify CORS headers are in the response (check Network tab)
- ✅ Ensure `add_cors_headers()` is called for all responses
- ✅ Check that preflight OPTIONS requests return 200 OK
- ✅ Verify the tracking endpoint URL is accessible from browser

### ngrok Session Expires
- Free ngrok URLs change every time you restart ngrok
- For persistent URLs, upgrade to paid plan
- Or use deployment for production

### Django ALLOWED_HOSTS Error
Add your public domain to settings:
```python
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'your-ngrok-url.ngrok.io',
    'your-production-domain.com'
]
```

### Database Issues After Deployment
- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Ensure environment variables are set correctly

## Summary

**For Development/Testing:**
- ✅ Use ngrok to expose localhost (quick & easy)
- ✅ Free tier available with changing URLs

**For Production:**
- ✅ Deploy to Railway, Heroku, DigitalOcean, or AWS
- ✅ Use environment variables for secrets
- ✅ Configure database and static files
- ✅ Set up SSL/HTTPS

**Current Status:**
- ✅ CORS headers are now added to all tracking endpoints
- ✅ Both script endpoint and tracking endpoint support cross-origin requests
- ✅ Preflight OPTIONS requests are handled correctly

The CORS issue is **fixed in the code**. Now you just need a **public URL** for your URL Monitor so your deployed site can reach it!
