# Upstash Redis Setup Instructions

## Important: Update Your .env File

Add these environment variables to your `.env` file (DO NOT commit this file):

```bash
# Upstash Redis Configuration
UPSTASH_REDIS_URL=https://your-redis-url.upstash.io
UPSTASH_REDIS_TOKEN=your-upstash-redis-token-here
```

## Steps to Get Upstash Credentials

1. **Sign up for Upstash** (if you haven't already):
   - Go to https://console.upstash.com/
   - Create a free account

2. **Create a Redis Database**:
   - Click "Create Database"
   - Choose a region (select closest to your Render deployment)
   - Select "Free" tier
   - Enable "REST API" (this is what we'll use)

3. **Get Your Credentials**:
   - After creating the database, go to the "Details" tab
   - Copy the "REST API" section:
     - **UPSTASH_REDIS_REST_URL** → This is your `UPSTASH_REDIS_URL`
     - **UPSTASH_REDIS_REST_TOKEN** → This is your `UPSTASH_REDIS_TOKEN`

## Update Render Environment Variables

On Render.com, add these environment variables to your web service:

1. Go to your web service dashboard
2. Click "Environment" in the left sidebar
3. Add these variables:
   ```
   UPSTASH_REDIS_URL = https://your-redis-url.upstash.io
   UPSTASH_REDIS_TOKEN = your-upstash-redis-token-here
   ```

## Update Render.yaml (if using Infrastructure as Code)

If you're using `render.yaml`, update it to include the Upstash environment variables:

```yaml
services:
  - type: web
    name: url-monitor
    env: python
    envVars:
      - key: UPSTASH_REDIS_URL
        sync: false  # Set manually in Render dashboard
      - key: UPSTASH_REDIS_TOKEN
        sync: false  # Set manually in Render dashboard
```

## Remove Old Redis Service (Optional)

If you were using Render's Redis service, you can now remove it since Upstash is more reliable for free tier deployments.

## Why Upstash?

- ✅ **HTTP-based**: Works better with serverless/free tier
- ✅ **No connection pooling issues**: No timeout errors
- ✅ **Better free tier**: More reliable than Render's free Redis
- ✅ **Global edge network**: Faster response times
- ✅ **Pay-per-request**: Only charged for actual usage

## Testing

After deploying with Upstash credentials:

1. Login should work without 500 errors
2. Manual URL checks should work
3. Celery tasks should execute properly
4. No "Connection refused" errors in logs

## Security Notes

- ⚠️ **NEVER** commit `.env` file to Git
- ⚠️ **NEVER** hardcode credentials in `settings.py`
- ✅ Always use environment variables
- ✅ Keep `.env` in `.gitignore`
