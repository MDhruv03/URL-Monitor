web: gunicorn url_monitor.wsgi:application --bind 0.0.0.0:$PORT
worker: python start_celery.py
