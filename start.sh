#!/bin/bash#!/bin/bash

set -eset -e



echo "=========================================="echo "=========================================="

echo "Starting URL Monitor Application"echo "Starting URL Monitor Application"

echo "=========================================="echo "=========================================="



# Wait for database to be available# Wait for database to be available

echo "→ Waiting for database connection..."echo "→ Waiting for database connection..."

max_attempts=30max_attempts=30

attempt=0attempt=0



while [ $attempt -lt $max_attempts ]; dowhile [ $attempt -lt $max_attempts ]; do

    attempt=$((attempt + 1))    attempt=$((attempt + 1))

    echo "⏳ Connection attempt $attempt/$max_attempts..."    echo "⏳ Connection attempt $attempt/$max_attempts..."

    

    if python manage.py migrate --check 2>/dev/null; then    if python manage.py migrate --check 2>/dev/null; then

        echo "✅ Database is ready!"        echo "✅ Database is ready!"

        break        break

    else    else

        if [ $attempt -lt $max_attempts ]; then        if [ $attempt -lt $max_attempts ]; then

            echo "⚠️  Database not ready yet, waiting 2 seconds..."            echo "⚠️  Database not ready yet, waiting 2 seconds..."

            sleep 2            sleep 2

        else        else

            echo "⚠️  Database connection timeout, attempting migrations anyway..."                 echo "⚠️  Database connection timeout, attempting migrations anyway..."

        fi        fi

    fi    fi

donedone



# Run migrations# Run migrations

echo "→ Running database migrations..."echo "→ Running database migrations..."

if python manage.py migrate --noinput; thenif python manage.py migrate --noinput; then

    echo "✅ Migrations completed successfully!"    echo "✅ Migrations completed successfully!"

elseelse

    echo "❌ Migration failed! Starting server anyway..."    echo "❌ Migration failed! Starting server anyway..."

    echo "Tables may not exist. Check DATABASE_URL configuration."    echo "Tables may not exist. Check DATABASE_URL configuration."

fifi



# Show applied migrations# Show applied migrations

echo "→ Applied migrations:"echo "→ Applied migrations:"

python manage.py showmigrations --plan | grep '\[X\]' | head -10python manage.py showmigrations --plan | grep '\[X\]' | head -10

echo "..."echo "..."



# Start Gunicorn# Start Gunicorn

echo "→ Starting Gunicorn server on port ${PORT:-8000}..."echo "→ Starting Gunicorn server on port ${PORT:-8000}..."

echo "=========================================="echo "=========================================="

exec gunicorn --bind 0.0.0.0:${PORT:-8000} \exec gunicorn --bind 0.0.0.0:${PORT:-8000} \

    --workers 3 \    --workers 3 \

    --timeout 120 \    --timeout 120 \

    --access-logfile - \    --access-logfile - \

    --error-logfile - \    --error-logfile - \

    --log-level info \    --log-level info \

    url_monitor.wsgi:application    url_monitor.wsgi:application

