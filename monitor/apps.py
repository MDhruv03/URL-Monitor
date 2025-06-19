from django.apps import AppConfig
import sys

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        # Avoid running on `makemigrations`, `migrate`, etc.
        if 'runserver' in sys.argv or 'celery' in sys.argv:
            from .tasks import schedule_checks
            # optional: run only once or under DEBUG
            # from django.conf import settings
            # if settings.DEBUG:
