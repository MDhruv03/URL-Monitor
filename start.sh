#!/bin/bash
set -e

echo "=========================================="
echo "Starting URL Monitor Application"
echo "=========================================="

# Wait for database to be available
echo "→ Waiting for database connection..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "⏳ Connection attempt $attempt/$max_attempts..."
    
    if python manage.py migrate --check 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    else
        if [ $attempt -lt $max_attempts ]; then
            echo "⚠️  Database not ready yet, waiting 2 seconds..."
            sleep 2
        else
            echo "⚠️  Database connection timeout, attempting migrations anyway..."
        fi
    fi
done

# Run migrations
echo "→ Running database migrations..."
if python manage.py migrate --noinput; then
    echo "✅ Migrations completed successfully!"
else
    echo "❌ Migration failed! Starting server anyway..."
    echo "Tables may not exist. Check DATABASE_URL configuration."
fi

# Show applied migrations
echo "→ Applied migrations:"
python manage.py showmigrations --plan | grep '\[X\]' | head -10
echo "..."

# Start Gunicorn
echo "→ Starting Gunicorn server on port ${PORT:-8000}..."
echo "=========================================="
exec gunicorn --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    url_monitor.wsgi:application