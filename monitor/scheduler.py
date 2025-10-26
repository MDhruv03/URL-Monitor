"""
Standalone URL Monitor - No Celery Required
Runs URL checks in background threads without external dependencies
"""
import threading
import time
import logging
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

class URLMonitorScheduler:
    """Background scheduler that runs URL checks without Celery"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("URL Monitor Scheduler started")
        
    def stop(self):
        """Stop the background scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("URL Monitor Scheduler stopped")
        
    def _run_scheduler(self):
        """Main scheduler loop - checks URLs periodically"""
        from monitor.models import MonitoredURL
        from monitor.tasks import check_url_status
        
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Get all active URLs that need checking
                now = timezone.now()
                urls_to_check = MonitoredURL.objects.filter(is_active=True)
                
                for url in urls_to_check:
                    try:
                        # Check if URL is due for checking
                        if url.last_checked:
                            time_since_check = (now - url.last_checked).total_seconds() / 60
                            if time_since_check < url.check_frequency:
                                continue  # Not due yet
                        
                        # Run check in separate thread to avoid blocking
                        check_thread = threading.Thread(
                            target=self._check_url,
                            args=(url,),
                            daemon=True
                        )
                        check_thread.start()
                        
                    except Exception as e:
                        logger.error(f"Error scheduling check for {url.url}: {e}")
                
                # Sleep for 30 seconds before next iteration
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_url(self, url):
        """Execute URL check (runs in separate thread)"""
        from monitor.tasks import check_url_status
        
        try:
            # Import here to avoid circular imports
            import requests
            from monitor.models import URLStatus, Alert
            from django.db import connection
            
            # Close old database connections (important for threads)
            connection.close()
            
            logger.info(f"Checking URL: {url.url}")
            
            # Perform the actual HTTP check
            start_time = time.time()
            try:
                response = requests.get(
                    url.url,
                    timeout=10,
                    allow_redirects=True,
                    verify=True
                )
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                status_code = response.status_code
                is_up = (status_code == url.expected_status)
                
            except requests.exceptions.Timeout:
                response_time = 10000
                status_code = 0
                is_up = False
                logger.warning(f"Timeout checking {url.url}")
                
            except Exception as e:
                response_time = 0
                status_code = 0
                is_up = False
                logger.error(f"Error checking {url.url}: {e}")
            
            # Save status to database
            URLStatus.objects.create(
                url=url,
                is_up=is_up,
                status_code=status_code,
                response_time=response_time,
                checked_at=timezone.now()
            )
            
            # Update URL's last_checked timestamp
            url.last_checked = timezone.now()
            url.save(update_fields=['last_checked'])
            
            # Send alert if URL is down
            if not is_up:
                try:
                    from monitor.tasks import send_alert
                    send_alert(str(url.id), f"URL is down (Status: {status_code})")
                except Exception as alert_error:
                    logger.error(f"Failed to send alert: {alert_error}")
            
            logger.info(f"Check completed: {url.url} - Status: {status_code}, Up: {is_up}")
            
        except Exception as e:
            logger.error(f"Fatal error in _check_url for {url.url}: {e}", exc_info=True)
        finally:
            # Always close connection after thread work
            connection.close()


# Global scheduler instance
_scheduler = None

def start_scheduler():
    """Initialize and start the global scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = URLMonitorScheduler()
        _scheduler.start()
    return _scheduler

def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None

def get_scheduler():
    """Get the scheduler instance (creates if doesn't exist)"""
    global _scheduler
    if _scheduler is None:
        start_scheduler()
    return _scheduler
