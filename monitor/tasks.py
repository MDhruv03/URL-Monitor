from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import requests
import time
from .models import MonitoredURL, URLStatus, Alert, Notification
import json
import logging
from uuid import UUID
logger = logging.getLogger(__name__)

@shared_task
def check_url_status(url_id):
    """
    Checks a single URL's status.
    Called by schedule_checks() or manually triggered.
    """
    logger.info(f"[CELERY WORKER] check_url_status started for url_id={url_id}")

    try:
        url = MonitoredURL.objects.get(id=UUID(url_id), is_active=True)
    except MonitoredURL.DoesNotExist:
        logger.warning(f"[CELERY WORKER] URL with id {url_id} not found or inactive")
        return {'error': 'URL not found'}
    
    logger.info(f"[CELERY WORKER] Checking {url.name} - {url.url}")
    
    start_time = time.time()
    try:
        response = requests.get(
            url.url,
            timeout=10,
            verify=url.check_ssl,
            headers={'User-Agent': 'URLMonitor/1.0'}
        )
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        status_code = response.status_code
        is_up = (status_code == url.expected_status and 
                response_time <= url.response_time_threshold)
        error_message = None
        
        logger.info(f"[CELERY WORKER] {url.name} - Status: {status_code}, Response: {response_time:.0f}ms, Up: {is_up}")
        
    except requests.exceptions.RequestException as e:
        response_time = 0
        status_code = 0
        is_up = False
        error_message = str(e)
        logger.error(f"[CELERY WORKER] {url.name} - Error: {error_message}")
    
    # Save the status
    url_status = URLStatus.objects.create(
        url=url,
        status_code=status_code,
        response_time=response_time,
        is_up=is_up,
        error_message=error_message
    )
    
    logger.info(f"[CELERY WORKER] URLStatus saved: ID={url_status.id}")
    
    # Check if we need to send alerts
    if not is_up:
        logger.info(f"[CELERY WORKER] URL is DOWN, triggering alert")
        send_alert.delay(url_status.id)
    
    return {
        'url': url.url,
        'status_code': status_code,
        'response_time': response_time,
        'is_up': is_up
    }

@shared_task
def send_alert(url_status_id):
    try:
        url_status = URLStatus.objects.get(id=url_status_id)
    except URLStatus.DoesNotExist:
        return
    
    url = url_status.url
    alerts = Alert.objects.filter(url=url, is_active=True)
    
    for alert in alerts:
        message = f"Alert: {url.name} ({url.url}) is DOWN\n"
        message += f"Status: {url_status.status_code if url_status.status_code != 0 else 'Connection Error'}\n"
        message += f"Response Time: {url_status.response_time:.2f}ms\n"
        message += f"Error: {url_status.error_message or 'None'}\n"
        message += f"Time: {url_status.timestamp}\n"
        
        # Create notification
        Notification.objects.create(
            user=alert.user,
            message=f"{url.name} is DOWN",
            url_status=url_status
        )
        
        if alert.method == 'email':
            try:
                send_mail(
                    f"URL Monitor Alert: {url.name} is DOWN",
                    message,
                    settings.EMAIL_HOST_USER,
                    [alert.destination],
                    fail_silently=False,
                )
                alert.last_sent = timezone.now()
                alert.save()
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        elif alert.method == 'telegram' and hasattr(settings, 'TELEGRAM_BOT_TOKEN'):
            try:
                import telegram
                bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
                bot.send_message(
                    chat_id=alert.destination,
                    text=message
                )
                alert.last_sent = timezone.now()
                alert.save()
            except Exception as e:
                logger.error(f"Failed to send Telegram alert: {e}")
        
        elif alert.method == 'slack' and hasattr(settings, 'SLACK_WEBHOOK_URL'):
            try:
                payload = {
                    "text": message,
                    "username": "URL Monitor",
                    "icon_emoji": ":warning:"
                }
                requests.post(
                    settings.SLACK_WEBHOOK_URL,
                    json=payload,
                    timeout=5
                )
                alert.last_sent = timezone.now()
                alert.save()
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")

@shared_task
def schedule_checks():
    """
    Called by Celery Beat every 60 seconds.
    Checks all active URLs that need to be checked based on their frequency.
    """
    logger.info("[CELERY BEAT] Running schedule_checks task")
    
    urls = MonitoredURL.objects.filter(is_active=True)
    checked_count = 0
    
    for url in urls:
        # Check if enough time has passed since last check
        last_status = URLStatus.objects.filter(url=url).order_by('-timestamp').first()
        
        if last_status:
            time_since_check = (timezone.now() - last_status.timestamp).total_seconds() / 60
            if time_since_check < url.frequency:
                logger.debug(f"[SKIP] {url.name} - Checked {time_since_check:.1f}min ago, frequency is {url.frequency}min")
                continue
        
        # Time to check this URL
        logger.info(f"[QUEUE] Checking {url.name} ({url.url})")
        check_url_status.delay(str(url.id))
        checked_count += 1
    
    logger.info(f"[CELERY BEAT] Queued {checked_count} URL checks")
    return f"Queued {checked_count} checks"