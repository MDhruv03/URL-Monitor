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

# Run migrations (will fail on first build if DB not ready)
echo "→ Running database migrations..."
if python manage.py migrate --check; then
    echo "✅ Migrations check passed, running migrations..."
    python manage.py migrate
else
    echo "⚠️  Migrations check failed, attempting to run anyway..."
    python manage.py migrate || echo "⚠️  Migrations failed - this is expected on first deploy. Redeploy after DB is ready."
fi

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
