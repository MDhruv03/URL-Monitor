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

# Wait for database to be ready (Render free tier)
echo "→ Waiting for database connection..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if python manage.py migrate --check 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    else
        attempt=$((attempt + 1))
        echo "⏳ Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Database connection timeout after $max_attempts attempts"
    echo "This usually means the PostgreSQL service isn't ready yet."
    echo "The web service will start, but migrations won't be applied."
    echo "Please trigger a manual redeploy after the database is ready."
    exit 1
fi

# Run migrations
echo "→ Running database migrations..."
python manage.py migrate --noinput

# Verify migrations were applied
echo "→ Verifying migrations..."
python manage.py showmigrations

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
