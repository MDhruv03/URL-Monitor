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


class PageView(models.Model):
    """Track individual page views with detailed analytics"""
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='page_views')
    session_id = models.CharField(max_length=100, db_index=True)
    visitor_id = models.CharField(max_length=100, db_index=True)  # Anonymous unique identifier
    
    # Page info
    page_url = models.CharField(max_length=500)
    page_title = models.CharField(max_length=200, blank=True)
    referrer = models.CharField(max_length=500, blank=True)
    
    # Time tracking
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    time_on_page = models.FloatField(default=0)  # Seconds
    
    # Engagement metrics
    scroll_depth = models.FloatField(default=0)  # Percentage 0-100
    scroll_events = models.JSONField(default=list)  # [{depth: 25, timestamp: ...}, ...]
    click_count = models.IntegerField(default=0)
    
    # Device & Browser
    user_agent = models.CharField(max_length=500, blank=True)
    device_type = models.CharField(max_length=20, default='desktop')  # desktop, mobile, tablet
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)  # 1920x1080
    
    # Geolocation
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['url', '-timestamp']),
            models.Index(fields=['session_id', '-timestamp']),
            models.Index(fields=['visitor_id', '-timestamp']),
            models.Index(fields=['country_code', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.page_url} - {self.timestamp}"


class ClickHeatmap(models.Model):
    """Track click positions for heatmap visualization"""
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='click_heatmaps')
    page_url = models.CharField(max_length=500, db_index=True)
    
    # Click coordinates
    x_position = models.IntegerField()  # X coordinate
    y_position = models.IntegerField()  # Y coordinate
    viewport_width = models.IntegerField()  # Viewport width at time of click
    viewport_height = models.IntegerField()  # Viewport height at time of click
    
    # Element info
    element_tag = models.CharField(max_length=50, blank=True)  # button, a, div, etc.
    element_id = models.CharField(max_length=100, blank=True)
    element_class = models.CharField(max_length=200, blank=True)
    element_text = models.CharField(max_length=200, blank=True)
    
    # Session info
    session_id = models.CharField(max_length=100, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    device_type = models.CharField(max_length=20, default='desktop')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['url', 'page_url', '-timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Click at ({self.x_position}, {self.y_position}) on {self.page_url}"


class ScrollHeatmap(models.Model):
    """Track scroll depth distribution for heatmap visualization"""
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='scroll_heatmaps')
    page_url = models.CharField(max_length=500, db_index=True)
    
    # Scroll data - JSON with depth ranges and counts
    # {0-10: 100, 10-20: 95, 20-30: 87, ...}
    depth_distribution = models.JSONField(default=dict)
    
    # Aggregation info
    date = models.DateField(db_index=True)
    total_views = models.IntegerField(default=0)
    average_depth = models.FloatField(default=0)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['url', 'page_url', 'date']
        indexes = [
            models.Index(fields=['url', '-date']),
        ]
    
    def __str__(self):
        return f"Scroll heatmap for {self.page_url} on {self.date}"


class MouseMovement(models.Model):
    """Track mouse movement patterns (rage clicks, dead clicks, etc.)"""
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='mouse_movements')
    session_id = models.CharField(max_length=100, db_index=True)
    page_url = models.CharField(max_length=500)
    
    # Movement type
    MOVEMENT_TYPES = [
        ('rage_click', 'Rage Click'),  # Multiple rapid clicks in same area
        ('dead_click', 'Dead Click'),  # Click with no response
        ('error_click', 'Error Click'),  # Click that caused an error
        ('hover', 'Extended Hover'),  # Long hover suggesting confusion
    ]
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, db_index=True)
    
    # Position data
    x_position = models.IntegerField()
    y_position = models.IntegerField()
    
    # Additional context
    click_count = models.IntegerField(default=1)  # For rage clicks
    element_selector = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['url', 'movement_type', '-timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} on {self.page_url}"


class SessionRecording(models.Model):
    """Store session replay data"""
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='session_recordings')
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    visitor_id = models.CharField(max_length=100, db_index=True)
    
    # Session info
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(default=0)  # Seconds
    
    # Events data - stored as compressed JSON
    events = models.JSONField(default=list)  # Interaction events timeline
    
    # Summary metrics
    pages_visited = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_scrolls = models.IntegerField(default=0)
    had_errors = models.BooleanField(default=False)
    had_rage_clicks = models.BooleanField(default=False)
    
    # Device info
    device_type = models.CharField(max_length=20, default='desktop')
    browser = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['url', '-start_time']),
            models.Index(fields=['visitor_id', '-start_time']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id[:8]} - {self.start_time}"


class PerformanceMetric(models.Model):
    """Track page performance metrics"""
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='performance_metrics')
    page_url = models.CharField(max_length=500)
    session_id = models.CharField(max_length=100, db_index=True)
    
    # Core Web Vitals
    first_contentful_paint = models.FloatField(null=True, blank=True)  # FCP in ms
    largest_contentful_paint = models.FloatField(null=True, blank=True)  # LCP in ms
    first_input_delay = models.FloatField(null=True, blank=True)  # FID in ms
    cumulative_layout_shift = models.FloatField(null=True, blank=True)  # CLS score
    time_to_interactive = models.FloatField(null=True, blank=True)  # TTI in ms
    
    # Additional metrics
    dom_load_time = models.FloatField(null=True, blank=True)  # ms
    page_load_time = models.FloatField(null=True, blank=True)  # ms
    resource_load_time = models.FloatField(null=True, blank=True)  # ms
    
    # Network
    connection_type = models.CharField(max_length=20, blank=True)  # 4g, wifi, etc.
    effective_bandwidth = models.FloatField(null=True, blank=True)  # Mbps
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['url', '-timestamp']),
            models.Index(fields=['page_url', '-timestamp']),
        ]
    
    def __str__(self):
        return f"Performance metrics for {self.page_url}"


class ConversionFunnel(models.Model):
    """Track conversion funnel steps"""
    url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name='conversion_funnels')
    name = models.CharField(max_length=100)
    steps = models.JSONField()  # [{'name': 'Landing', 'url': '/'}, {'name': 'Signup', 'url': '/signup'}]
    
    # Aggregated data
    date = models.DateField(db_index=True)
    step_completion = models.JSONField()  # {'0': 1000, '1': 450, '2': 123}
    conversion_rate = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['url', 'name', 'date']
        indexes = [
            models.Index(fields=['url', '-date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.date}"
        indexes = [
            models.Index(fields=['url', '-timestamp']),
        ]   

