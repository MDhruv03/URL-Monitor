from django.apps import AppConfig
import sys
import os

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        # Only start scheduler in production (gunicorn) or development (runserver)
        # Skip during migrations, shell, etc.
        if 'runserver' in sys.argv or 'gunicorn' in os.environ.get('SERVER_SOFTWARE', ''):
            try:
                from .scheduler import start_scheduler
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Starting background URL monitor scheduler...")
                start_scheduler()
                logger.info("Background scheduler started successfully")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to start scheduler: {e}")
