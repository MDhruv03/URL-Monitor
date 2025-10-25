@echo off
REM Windows build script for local testing
REM On Render, use build.sh instead

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

echo Collecting static files...
python manage.py collectstatic --no-input

echo Running migrations...
python manage.py migrate

echo Build complete!
