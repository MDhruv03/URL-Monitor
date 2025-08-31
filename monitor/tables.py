import django_tables2 as tables
from django.utils.html import format_html
from .models import URLStatus, Alert, Notification, MonitoredURL
from django.urls import reverse

class URLTable(tables.Table):
    name = tables.Column(linkify=False)
    status = tables.Column(empty_values=(), orderable=False)
    actions = tables.Column(empty_values=(), orderable=False)
    
    class Meta:
        model = MonitoredURL
        fields = ('name', 'url', 'frequency', 'status', 'actions')
        attrs = {
            'class': 'table table-dark table-hover',
            'thead': {'class': 'thead-light'}
        }
    
    def render_status(self, value, record):
        latest = record.statuses.first()
        if latest:
            if latest.is_up:
                return format_html('<span class="badge bg-success">UP</span>')
            else:
                return format_html('<span class="badge bg-danger">DOWN</span>')
        return format_html('<span class="badge bg-secondary">UNKNOWN</span>')
    
    def render_actions(self, value, record):
        return format_html(
             '''
        <div class="btn-group">
            <a href="{}" class="btn btn-sm btn-info">Status</a>
            <button type="button" class="btn btn-sm btn-info dropdown-toggle dropdown-toggle-split" 
                    data-bs-toggle="dropdown">
            </button>
            <div class="dropdown-menu">
                <a class="dropdown-item" href="{}">Traffic</a>
                <a class="dropdown-item" href="{}">User Flows</a>
                <a class="dropdown-item" href="{}">Engagement</a>
                '<a href="{}" class="btn btn-sm btn-info">Check Now</a> '
            '<a href="{}" class="btn btn-sm btn-warning">Edit</a> '
            '<a href="{}" class="btn btn-sm btn-danger">Delete</a>',
        </div>
        ''',
        reverse('monitor:url_detail', args=[record.id]),
        reverse('monitor:traffic_dashboard', args=[record.id]),
        reverse('monitor:user_flows', args=[record.id]),
        reverse('monitor:engagement_metrics', args=[record.id]),
        reverse('monitor:check_now', args=[record.id]),
        reverse('monitor:edit_url', args=[record.id]),
        reverse('monitor:delete_url', args=[record.id])
        )

class StatusTable(tables.Table):
    timestamp = tables.DateTimeColumn(format='Y-m-d H:i:s')
    is_up = tables.Column(empty_values=(), verbose_name="Status")
    response_time = tables.Column(verbose_name="Response (ms)")
    
    class Meta:
        model = URLStatus
        fields = ('timestamp', 'is_up', 'status_code', 'response_time', 'error_message')
        attrs = {
            'class': 'table table-dark table-hover',
            'thead': {'class': 'thead-light'}
        }
    
    def render_is_up(self, value, record):
        if record.is_up:
            return format_html('<span class="badge bg-success">UP</span>')
        return format_html('<span class="badge bg-danger">DOWN</span>')
    
    def render_response_time(self, value):
        return f"{value:.2f}"

class AlertTable(tables.Table):
    actions = tables.Column(empty_values=(), orderable=False)
    
    class Meta:
        model = Alert
        fields = ('url', 'method', 'destination', 'is_active', 'last_sent', 'actions')
        attrs = {
            'class': 'table table-dark table-hover',
            'thead': {'class': 'thead-light'}
        }
    
    def render_method(self, value):
        return value.capitalize()
    
    def render_actions(self, value, record):
        return format_html(
            '<a href="{}" class="btn btn-sm btn-danger">Delete</a>',
            reverse('monitor:delete_alert', args=[record.id])
        )

class NotificationTable(tables.Table):
    message = tables.Column(linkify=False)
    created_at = tables.DateTimeColumn(format='Y-m-d H:i:s')
    is_read = tables.BooleanColumn(verbose_name="Read")
    
    class Meta:
        model = Notification
        fields = ('message', 'created_at', 'is_read')
        attrs = {
            'class': 'table table-dark table-hover',
            'thead': {'class': 'thead-light'}
        }
    
    def render_is_read(self, value):
        if value:
            return format_html('<i class="bi bi-check-circle-fill text-success"></i>')
        return format_html('<i class="bi bi-exclamation-circle-fill text-warning"></i>')