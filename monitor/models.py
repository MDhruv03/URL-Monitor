from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from django.urls import reverse

class MonitoredURL(models.Model):
    FREQUENCY_CHOICES = [
        (1, '1 minute'),
        (5, '5 minutes'),
        (10, '10 minutes'),
        (30, '30 minutes'),
        (60, '1 hour'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(max_length=500)
    name = models.CharField(max_length=100)
    frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    response_time_threshold = models.IntegerField(
        default=500,  # milliseconds
        validators=[MinValueValidator(100), MaxValueValidator(20000)],
        help_text="Response time threshold in milliseconds"
    )
    expected_status = models.IntegerField(
        default=200,
        validators=[MinValueValidator(100), MaxValueValidator(599)]
    )
    check_ssl = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    def get_absolute_url(self):
        return reverse('monitor:url_detail', args=[self.id])

class URLStatus(models.Model):
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='statuses')
    timestamp = models.DateTimeField(default=timezone.now)
    status_code = models.IntegerField()
    response_time = models.FloatField()  # in milliseconds
    is_up = models.BooleanField()
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return f"{self.url.name} - {'UP' if self.is_up else 'DOWN'} at {self.timestamp}"

class Alert(models.Model):
    ALERT_METHODS = [
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('slack', 'Slack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=ALERT_METHODS)
    destination = models.CharField(max_length=255)  # email, webhook URL, etc.
    last_sent = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_method_display()} alert for {self.url.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    url_status = models.ForeignKey(URLStatus, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."