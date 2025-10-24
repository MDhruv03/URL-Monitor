@echo off
REM Development startup script for URL Monitor

echo Starting URL Monitor Development Environment...
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Error: Virtual environment not activated!
    echo Please run: venv\Scripts\activate
    pause
    exit /b 1
)

REM Check if Redis is running
echo Checking Redis connection...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo Error: Redis is not running!
    echo Please start Redis server first.
    pause
    exit /b 1
)

echo Redis is running ✓
echo.

REM Start Celery Worker in new window
echo Starting Celery Worker...
start "Celery Worker" cmd /k "celery -A url_monitor worker -l info --pool=solo"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Celery Beat in new window
echo Starting Celery Beat...
start "Celery Beat" cmd /k "celery -A url_monitor beat -l info"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Django development server
echo Starting Django Development Server...
echo.
python manage.py runserver

REM If Django server stops, cleanup
echo.
echo Shutting down...
taskkill /FI "WindowTitle eq Celery*" /T /F >nul 2>&1
