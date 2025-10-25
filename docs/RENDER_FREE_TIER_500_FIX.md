# 🚨 500 Error After Registration - RENDER FREE TIER FIX

## ⚠️ Important
**Render Free Tier = NO Shell Access**  
You CANNOT run `python manage.py migrate` manually.  
Migrations must happen during BUILD automatically.

---

## 🎯 The Real Problem

Your web service built **BEFORE** PostgreSQL was ready.  
Result: Migrations didn't run → Database tables don't exist → 500 error.

---

## ✅ THE FIX (Takes 5 Minutes)

### Step 1: Check Database Status
1. Go to: https://dashboard.render.com
2. Look at your services:
   - `url-monitor-db` (PostgreSQL) - Is it "Available"? ✅
   - `url-monitor-redis` (Redis) - Is it "Available"? ✅
   - `url-monitor` (Web) - Is it "Live"? ✅

### Step 2: Trigger Manual Redeploy
1. Click on **"url-monitor"** web service
2. Click **"Manual Deploy"** button (top right)
3. Select: **"Clear build cache & deploy"**
4. Click **"Deploy"**

### Step 3: Watch Build Logs
Look for this in build output:
```
✅ GOOD:
→ Running database migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, monitor
Running migrations:
  Applying monitor.0001_initial... OK
  Applying monitor.0002_... OK
  [All migrations applied successfully]
```

### Step 4: Test
After deploy completes (5-10 min):
- Go to: `https://url-monitor-2xlk.onrender.com/register/`
- Register a new account
- Should work now! ✅

---

## 🔍 Why This Happens

**First Deployment Timeline:**
```
0 min: Deploy starts
1 min: PostgreSQL starts creating (takes 2-3 min)
2 min: Web service starts building
3 min: Build runs migrations → PostgreSQL not ready yet → Fails
4 min: Web service goes "Live" but no database tables
5 min: PostgreSQL finally ready (too late!)
```

**Second Deployment (Redeploy):**
```
0 min: Manual deploy starts
1 min: PostgreSQL already ready ✅
2 min: Build runs migrations → Success! ✅
5 min: Web service "Live" with database tables ✅
```

---

## 📋 Quick Checklist

Before manual redeploy:
- [ ] PostgreSQL shows "Available" (not "Creating")
- [ ] Redis shows "Available"
- [ ] `ALLOWED_HOSTS=url-monitor-2xlk.onrender.com` is set

After manual redeploy:
- [ ] Build logs show "Applying migrations... OK"
- [ ] Deploy status: "Deploy succeeded"
- [ ] Test registration → works without 500 error

---

## 🐛 Still Getting 500?

### Option 1: Check Actual Error
1. Environment tab → Set `DEBUG=True`
2. Wait for redeploy
3. Try registering → see full error page
4. **Change DEBUG back to False!**

### Option 2: Check Logs
1. Logs tab → look for Python traceback
2. Common errors:
   - `relation "monitor_monitoredurl" does not exist` → Redeploy again
   - `no such table` → Redeploy again
   - `OperationalError` → Database not connected

---

## 🎯 One-Line Summary

**Your build.sh is correct. Just redeploy now that database is ready.**

---

## 📚 Detailed Guide

See full documentation: `docs/FIX_500_ERROR.md`

---

**DO THIS NOW:**
1. https://dashboard.render.com
2. Click "url-monitor"
3. Click "Manual Deploy" → "Clear build cache & deploy"
4. Wait 5-10 minutes
5. Test: https://url-monitor-2xlk.onrender.com/register/
