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
    print(f"[CELERY] check_url_status task started with url_id={url_id}")

    try:
        url = MonitoredURL.objects.get(id=UUID(url_id), is_active=True)
    except MonitoredURL.DoesNotExist:
        print(f"[DEBUG] URL with id {url_id} not found.")
        return
    
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
    except requests.exceptions.RequestException as e:
        response_time = 0
        status_code = 0
        is_up = False
        error_message = str(e)
    
    # Save the status
    url_status = URLStatus.objects.create(
        url=url,
        status_code=status_code,
        response_time=response_time,
        is_up=is_up,
        error_message=error_message
    )
    
    # Check if we need to send alerts
    if not is_up:
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
    urls = MonitoredURL.objects.filter(is_active=True)
    for url in urls:
        check_url_status.apply_async(
            args=[str(url.id)],
            countdown=url.frequency * 60
        )