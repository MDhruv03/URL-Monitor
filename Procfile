web: gunicorn url_monitor.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A url_monitor worker --loglevel=info
beat: celery -A url_monitor beat --loglevel=info
