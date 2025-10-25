#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=========================================="
echo "Starting build process..."
echo "=========================================="

# Upgrade pip
echo "→ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "→ Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "→ Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations (with retry logic)
echo "→ Running database migrations..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "⏳ Migration attempt $attempt/$max_attempts..."
    
    if python manage.py migrate --noinput 2>&1; then
        echo "✅ Migrations completed successfully!"
        break
    else
        if [ $attempt -lt $max_attempts ]; then
            echo "⚠️  Migration attempt $attempt failed, retrying in 3 seconds..."
            sleep 3
        else
            echo "❌ All migration attempts failed after $max_attempts tries"
            echo "Database may not be ready or there's a configuration issue."
            echo "Check DATABASE_URL is set correctly."
            exit 1
        fi
    fi
done

# Verify migrations were applied
echo "→ Verifying migrations..."
python manage.py showmigrations

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
