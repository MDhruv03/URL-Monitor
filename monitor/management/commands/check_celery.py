from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check Celery worker status and test task execution'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Celery Status Check ===\n'))
        
        # Check Celery workers
        try:
            from celery import current_app
            inspect = current_app.control.inspect(timeout=2.0)
            
            # Check active workers
            active_workers = inspect.active()
            if active_workers:
                self.stdout.write(self.style.SUCCESS(f'✓ Celery workers running: {len(active_workers)}'))
                for worker_name, tasks in active_workers.items():
                    self.stdout.write(f'  - {worker_name}: {len(tasks)} active tasks')
            else:
                self.stdout.write(self.style.ERROR('✗ No active Celery workers found'))
                self.stdout.write(self.style.WARNING('\nTo start Celery worker, run:'))
                self.stdout.write('  celery -A url_monitor worker --loglevel=info')
            
            # Check registered tasks
            registered = inspect.registered()
            if registered:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Registered tasks found'))
                for worker_name, tasks in registered.items():
                    self.stdout.write(f'  Worker: {worker_name}')
                    for task in tasks:
                        if 'monitor' in task:
                            self.stdout.write(f'    - {task}')
            
            # Check scheduled tasks (beat)
            scheduled = inspect.scheduled()
            if scheduled:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Scheduled tasks: {sum(len(v) for v in scheduled.values())}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Celery connection failed: {e}'))
            self.stdout.write(self.style.WARNING('\nPossible issues:'))
            self.stdout.write('  1. Celery worker not running')
            self.stdout.write('  2. Redis connection issue (check CELERY_BROKER_URL)')
            self.stdout.write('  3. Network/firewall blocking Redis connection')
        
        # Test a simple URL check
        self.stdout.write(self.style.SUCCESS('\n=== Testing URL Check ==='))
        try:
            from monitor.models import MonitoredURL
            test_url = MonitoredURL.objects.filter(is_active=True).first()
            
            if test_url:
                self.stdout.write(f'Testing with URL: {test_url.name} ({test_url.url})')
                
                # Try synchronous check
                from monitor.tasks import check_url_status
                result = check_url_status(str(test_url.id))
                
                if result.get('is_up'):
                    self.stdout.write(self.style.SUCCESS(f'✓ URL is UP'))
                    self.stdout.write(f'  Status Code: {result.get("status_code")}')
                    self.stdout.write(f'  Response Time: {result.get("response_time"):.0f}ms')
                else:
                    self.stdout.write(self.style.ERROR(f'✗ URL is DOWN'))
                    
            else:
                self.stdout.write(self.style.WARNING('No monitored URLs found to test'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ URL check failed: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Check Complete ==='))
