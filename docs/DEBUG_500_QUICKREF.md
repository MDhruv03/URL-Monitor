# 🔍 Debugging 500 Error - Quick Reference

## v2.0.3: Debugging Tools Deployed ✅

### What's New
1. **Comprehensive logging** in registration endpoint
2. **Health check endpoint** at `/health/`
3. **Django logging** configured to output to Render logs

---

## 🏥 Step 1: Test Health Check (Do This First!)

```bash
curl https://url-monitor-2xlk.onrender.com/health/
```

### Expected Response:
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

### If You Get "unhealthy":
```json
{
  "status": "unhealthy",
  "error": "relation 'auth_user' does not exist",
  "message": "Database tables may not be initialized. Run migrations."
}
```

**This means:** Migrations didn't run during build.

**Fix:** Trigger manual redeploy with "Clear build cache & deploy"

---

## 📋 Step 2: Try Registration & Check Logs

### Try Registration:
1. Go to: `https://url-monitor-2xlk.onrender.com/register/`
2. Fill in form:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `TestPass123!`
   - Confirm Password: `TestPass123!`
3. Click Register

### Check Render Logs:

Go to: Render Dashboard → Logs tab

**Look for these log messages:**

#### ✅ Success Flow:
```
INFO Registration attempt - POST data: dict_keys(['username', 'email', 'password1', 'password2'])
INFO Form is valid, creating user: testuser
INFO User created successfully: testuser
INFO User logged in: testuser
```

#### ❌ Error Flow:
```
ERROR Registration error: relation "auth_user" does not exist
```

OR

```
WARNING Form validation failed: {"username": ["This field is required."]}
```

---

## 🐛 Common Errors & Fixes

### Error 1: `relation "auth_user" does not exist`
**Cause:** Database tables not created (migrations didn't run)

**Fix:**
1. Go to Render Dashboard
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"
4. Wait 5-10 minutes
5. Check `/health/` endpoint again

---

### Error 2: `FATAL: database "url_monitor" does not exist`
**Cause:** PostgreSQL database not provisioned

**Fix:**
1. Check Render Dashboard → Services
2. Verify `url-monitor-db` shows "Available"
3. Check Environment tab → DATABASE_URL is set
4. Redeploy web service

---

### Error 3: `Form validation failed`
**Cause:** Missing or invalid form fields

**Logs will show:**
```json
{
  "username": ["This field is required."],
  "password1": ["This password is too short."]
}
```

**Fix:** Check form fields match requirements:
- Username: Required, unique
- Email: Required, valid format, unique
- Password1: Required, min 8 chars
- Password2: Must match Password1

---

### Error 4: `connection refused` or `could not connect to server`
**Cause:** DATABASE_URL not set or PostgreSQL not ready

**Fix:**
1. Environment tab → Check DATABASE_URL exists
2. Should start with `postgres://` or `postgresql://`
3. Check `url-monitor-db` service is "Available"
4. Redeploy if database wasn't ready during first build

---

## 🔧 Debugging Commands

### Test Health Check:
```bash
curl https://url-monitor-2xlk.onrender.com/health/
```

### Test Registration (curl):
```bash
curl -X POST https://url-monitor-2xlk.onrender.com/register/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&email=test@example.com&password1=TestPass123!&password2=TestPass123!"
```

### Check Logs in Real-Time:
1. Render Dashboard → Logs tab
2. Keep window open
3. Try registration in another window
4. Watch logs appear in real-time

---

## ✅ Success Indicators

### Health Check Returns:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Registration Works:
- No 500 error
- Redirects to `/urls/` (URL list page)
- Logs show: "User created successfully"

### Render Logs Show:
```
INFO Registration attempt - POST data: ...
INFO Form is valid, creating user: testuser
INFO User created successfully: testuser
INFO User logged in: testuser
```

---

## 📊 Troubleshooting Flowchart

```
1. Test /health/ endpoint
   ├─ healthy? → Go to step 2
   └─ unhealthy? → Redeploy (migrations didn't run)

2. Try registration
   ├─ Works? → Success! 🎉
   └─ 500 error? → Go to step 3

3. Check Render logs
   ├─ "relation does not exist"? → Redeploy
   ├─ "Form validation failed"? → Fix form fields
   ├─ "could not connect"? → Check DATABASE_URL
   └─ Other error? → Share exact error message
```

---

## 🚀 Quick Fix Checklist

Before reporting issue, verify:

- [ ] Health check endpoint tested first
- [ ] PostgreSQL shows "Available" in Render
- [ ] DATABASE_URL is set in Environment tab
- [ ] ALLOWED_HOSTS includes domain
- [ ] Latest deploy shows "Deploy succeeded"
- [ ] Build logs show "Applying migrations... OK"
- [ ] Checked Render logs for exact error
- [ ] Tried registration after latest deployment

---

## 📝 Reporting Issues

If still getting 500 error, provide:

1. **Health check response:**
   ```bash
   curl https://url-monitor-2xlk.onrender.com/health/
   ```

2. **Exact error from Render logs:**
   - Go to Logs tab
   - Try registration
   - Copy the ERROR message with full traceback

3. **Build log snippet:**
   - Events tab → Latest deploy → View logs
   - Copy the migration section

4. **Environment check:**
   - Screenshot of Environment tab showing:
     - DATABASE_URL (present/not present)
     - ALLOWED_HOSTS value

---

**Current Status:** Debugging tools deployed, waiting for Render to finish deploying v2.0.3

**Next Step:** Test `/health/` endpoint after deployment completes
