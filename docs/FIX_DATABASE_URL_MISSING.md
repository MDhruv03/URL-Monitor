# 🚨 CRITICAL: DATABASE_URL Not Set in Render

## Root Cause Identified

Your application is using **SQLite instead of PostgreSQL** because the `DATABASE_URL` environment variable is **NOT set** in Render.

### Evidence from Logs:
```
File "/usr/local/lib/python3.11/site-packages/django/db/backends/sqlite3/base.py"
sqlite3.OperationalError: no such table: auth_user
```

The error path shows `sqlite3/base.py` - this proves Django is using SQLite (local dev database) instead of PostgreSQL (production database).

---

## Why This Happened

Your `settings.py` has this logic:

```python
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Use PostgreSQL (production)
    DATABASES = {'default': dj_database_url.config(...)}
else:
    # Use SQLite (local development)
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', ...}}
```

Since `DATABASE_URL` is not set, Django falls back to SQLite. SQLite has no tables because migrations never ran on it.

### Why render.yaml Didn't Work

Your `render.yaml` has this:

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: url-monitor-db
      property: connectionString
```

**Possible reasons the link didn't work:**
1. Blueprint created BEFORE database was provisioned
2. Database link wasn't established during initial deploy
3. Environment variables need manual sync after first deploy
4. render.yaml config only applies when creating NEW services

**Solution:** Manually set DATABASE_URL in the Render Dashboard (this overrides render.yaml).

---

## The Fix (Step-by-Step)

### Step 1: Go to Render Dashboard
Navigate to: **https://dashboard.render.com**

### Step 2: Select Your Web Service
Click on: **url-monitor** (the web service, not the database)

### Step 3: Open Environment Tab
Click on the **"Environment"** tab in the left sidebar

### Step 4: Add DATABASE_URL

**Method A: Link to Database (Recommended)**
1. Click **"Add Environment Variable"** button
2. In the "Key" field, type: `DATABASE_URL`
3. Click **"Link to Database"** (instead of typing a value)
4. From the dropdown, select: **url-monitor-db**
5. Click **"Link"**

**Method B: Manual Connection String (Alternative)**
1. First, go to **url-monitor-db** service
2. Find and copy the **"Internal Database URL"** (starts with `postgresql://`)
3. Go back to **url-monitor** web service → Environment tab
4. Click **"Add Environment Variable"**
5. Key: `DATABASE_URL`
6. Value: Paste the connection string you copied
7. Click **"Add"**

### Step 5: Save Changes
Click **"Save Changes"** button at the bottom

⚠️ **Important:** Saving environment variables triggers an automatic redeploy!

---

## What Happens After Setting DATABASE_URL

### Automatic Process:
1. ✅ Render detects environment variable change
2. ✅ Triggers automatic redeploy (5-10 minutes)
3. ✅ build.sh runs with DATABASE_URL set
4. ✅ Django connects to PostgreSQL (not SQLite)
5. ✅ Waits for PostgreSQL to be ready
6. ✅ Runs migrations → creates all tables
7. ✅ Web service starts successfully

### Expected Logs During Build:
```
→ Waiting for database connection...
⏳ Waiting for database... (attempt 1/30)
✅ Database is ready!
→ Running database migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, monitor, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  [... more migrations ...]
→ Verifying migrations...
[List of all applied migrations]
✅ Build completed successfully!
```

### Testing After Deployment:

**1. Health Check (should now show healthy)**
```bash
curl https://url-monitor-2xlk.onrender.com/health/
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "tables": {
    "users": 0,
    "monitored_urls": 0
  },
  "migrations": "applied"
}
```

**2. Registration (should now work)**
- Go to: `https://url-monitor-2xlk.onrender.com/register/`
- Fill in the form
- Submit
- ✅ Should redirect to URL list (no 500 error!)

**3. Login (should now work)**
- Go to: `https://url-monitor-2xlk.onrender.com/login/`
- Use credentials from registration
- ✅ Should log in successfully!

---

## Timeline

| Step | Duration | Status |
|------|----------|--------|
| Set DATABASE_URL in Render | 1-2 minutes | Manual action required |
| Render detects change | Immediate | Automatic |
| Build + Deploy | 5-10 minutes | Automatic |
| Test health check | 10 seconds | Manual verification |
| Test registration | 30 seconds | Manual verification |
| **Total Time** | **~10 minutes** | |

---

## Verification Checklist

After deployment completes, verify these items:

- [ ] Health check returns `"status": "healthy"`
- [ ] Health check shows `"database": "connected"`
- [ ] Health check shows table counts (users: 0, monitored_urls: 0)
- [ ] Registration page loads without errors
- [ ] Can submit registration form successfully
- [ ] Redirects to URL list after registration
- [ ] Can log in with newly created account
- [ ] Dashboard loads without 500 error

---

## Troubleshooting

### If build fails with "Database connection timeout"
**Problem:** PostgreSQL not ready yet

**Solution:**
1. Wait 2-3 minutes for database to fully start
2. Trigger manual redeploy: Dashboard → Manual Deploy → "Clear build cache & deploy"

### If still getting SQLite errors after setting DATABASE_URL
**Problem:** Environment variable not picked up

**Solution:**
1. Verify DATABASE_URL is listed in Environment tab
2. Check value starts with `postgresql://` (not `postgres://`)
3. Trigger manual redeploy to force reload

### If health check still returns "unhealthy"
**Problem:** Migrations didn't run

**Solution:**
1. Check build logs for migration errors
2. Look for "Running migrations... OK"
3. If missing, redeploy with "Clear build cache"

---

## Why This Is The Root Cause

All your errors trace back to this:

```
django.db.utils.OperationalError: no such table: auth_user
```

**Explanation:**
- `auth_user` is created by Django migrations
- Migrations run against the configured database
- Your configured database was SQLite (because DATABASE_URL wasn't set)
- SQLite was never migrated (only PostgreSQL should be)
- No tables = no registration, no login, no anything!

**The Fix:**
- Set DATABASE_URL → Django uses PostgreSQL
- Migrations create tables in PostgreSQL
- Everything works! ✅

---

## Summary

**Problem:** DATABASE_URL environment variable missing in Render
**Symptom:** Django using SQLite instead of PostgreSQL
**Result:** No database tables, causing all 500 errors
**Solution:** Set DATABASE_URL in Render Dashboard → Link to url-monitor-db
**Outcome:** PostgreSQL gets migrated, tables created, app works!

---

**Next Step:** Set DATABASE_URL in Render Dashboard NOW, then wait for redeploy to complete!
