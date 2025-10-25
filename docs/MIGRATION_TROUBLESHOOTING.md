# Alternative Migration Strategy

If the automatic migrations in `build.sh` aren't running, here are alternative approaches:

## Option 1: Check Build Command in render.yaml

Verify the build command is actually running build.sh:

```yaml
buildCommand: "chmod +x build.sh && ./build.sh"
```

## Option 2: Run Migrations via Render Shell (Paid Plans Only)

If you have access to Shell:
```bash
python manage.py migrate
```

## Option 3: Add Release Command

Render supports a `release` command that runs after build but before deploy.

Update your `render.yaml`:

```yaml
services:
  - type: web
    name: url-monitor
    env: python
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --no-input"
    # Add this line:
    preDeployCommand: "python manage.py migrate --noinput"
    startCommand: "gunicorn url_monitor.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120"
```

**Note:** `preDeployCommand` is only available on paid plans.

## Option 4: Simplify build.sh (Remove Wait Logic)

If the database wait logic is causing issues, try a simpler version:

```bash
#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate --noinput || echo "Migrations failed - database may not be ready"

echo "Build complete!"
```

## Option 5: Check Database Connection String

Verify DATABASE_URL format is correct. It should be:

```
postgresql://user:password@host:port/database
```

NOT:
```
postgres://user:password@host:port/database
```

Some versions of PostgreSQL URLs use `postgres://` instead of `postgresql://`. Django's `dj-database-url` handles both, but there might be issues.

## Option 6: Manual SQL Connection

If you have access to the database directly:

1. Get the external database URL from Render
2. Connect using psql or a GUI tool
3. Check if any tables exist:
   ```sql
   \dt
   ```
4. If no tables, something is preventing migrations

## Option 7: Check Environment Variables

Ensure these are set in Render:
- `DATABASE_URL` - should be set to PostgreSQL connection string
- `DEBUG` - should be `False` for production
- `ALLOWED_HOSTS` - should include your Render domain
- `SECRET_KEY` - should be set (auto-generated)

## Debugging Steps

### Check if migrations are detected:
```bash
python manage.py showmigrations
```

Expected output:
```
admin
 [ ] 0001_initial
 [ ] 0002_logentry_remove_auto_add
auth
 [ ] 0001_initial
...
```

### Check database connection:
```bash
python manage.py dbshell
```

Should connect to PostgreSQL without errors.

### Try running migrations manually:
```bash
python manage.py migrate --verbosity 3
```

Shows detailed migration output.

## Most Likely Issues

1. **Build command not running build.sh**
   - Check render.yaml buildCommand
   - Verify build.sh has execute permissions

2. **Database not ready when migrations run**
   - Database takes time to provision
   - Build might be timing out before DB is ready

3. **Wrong DATABASE_URL format**
   - Should start with `postgresql://`
   - Check connection string is complete

4. **Migrations files missing**
   - Verify `monitor/migrations/` exists
   - Verify `__init__.py` exists in migrations folder
   - Check git has committed migration files

## Next Steps

Please provide:
1. Full build logs from latest deploy
2. Output of checking DATABASE_URL value (without password)
3. Confirmation that you clicked "Clear build cache & deploy"
4. Any error messages from the build
