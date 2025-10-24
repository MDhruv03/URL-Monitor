from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from django.urls import reverse


class URLGroup(models.Model):
    """Group/Category for organizing monitored URLs"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class MonitoredURL(models.Model):
    FREQUENCY_CHOICES = [
        (1, '1 minute'),
        (5, '5 minutes'),
        (10, '10 minutes'),
        (30, '30 minutes'),
        (60, '1 hour'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    group = models.ForeignKey(URLGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='urls')
    url = models.URLField(max_length=500)
    name = models.CharField(max_length=100)
    frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=5)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
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
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    
    def get_absolute_url(self):
        return reverse('monitor:url_detail', args=[self.id])


class StatusPage(models.Model):
    """Public status page for sharing monitoring status"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=100)
    is_public = models.BooleanField(default=True)
    show_response_time = models.BooleanField(default=True)
    show_uptime_percentage = models.BooleanField(default=True)
    custom_domain = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Customization
    logo_url = models.URLField(blank=True, null=True)
    theme_color = models.CharField(max_length=7, default='#3B82F6')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_public_url(self):
        return reverse('monitor:public_status_page', args=[self.slug])


class StatusPageURL(models.Model):
    """URLs displayed on a status page"""
    status_page = models.ForeignKey(StatusPage, on_delete=models.CASCADE, related_name='monitored_urls')
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['status_page', 'url']
    
    def __str__(self):
        return f"{self.display_name or self.url.name} on {self.status_page.title}"


class URLStatus(models.Model):
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='statuses')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    status_code = models.IntegerField()
    response_time = models.FloatField()  # in milliseconds
    is_up = models.BooleanField(db_index=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
        indexes = [
            models.Index(fields=['url', '-timestamp']),
            models.Index(fields=['url', 'is_up', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.url.name} - {'UP' if self.is_up else 'DOWN'} at {self.timestamp}"

class Alert(models.Model):
    ALERT_METHODS = [
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('slack', 'Slack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=ALERT_METHODS)
    destination = models.CharField(max_length=255)  # email, webhook URL, etc.
    last_sent = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['url', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_method_display()} alert for {self.url.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    url_status = models.ForeignKey(URLStatus, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."
    
class TrafficMetric(models.Model):
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    requests = models.PositiveIntegerField()  # Total requests
    bandwidth = models.FloatField()  # In MB
    status_distribution = models.JSONField()  # {200: 85, 404: 2, 500: 1}
    unique_visitors = models.PositiveIntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['url', '-timestamp']),
        ]

class UserFlow(models.Model):
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, db_index=True)
    path_sequence = models.JSONField()  # ['/', '/products', '/checkout']
    timestamp_start = models.DateTimeField(db_index=True)
    timestamp_end = models.DateTimeField()
    exit_page = models.CharField(max_length=200)
    
    class Meta:
        indexes = [
            models.Index(fields=['url', '-timestamp_end']),
        ]

class Engagement(models.Model):
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, db_index=True)
    duration = models.FloatField()  # Seconds
    scroll_depth = models.FloatField()  # Percentage 0-100
    interactions = models.PositiveIntegerField()  # Clicks, form interactions
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['url', '-timestamp']),
        ]   

