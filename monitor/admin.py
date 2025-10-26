from django.contrib import admin
from monitor.models import (
    MonitoredURL, URLStatus, Alert, Notification,
    PageView, ClickHeatmap, MouseMovement,
    PerformanceMetric
)

@admin.register(MonitoredURL)
class MonitoredURLAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'user', 'is_active')
    list_filter = ('is_active', 'user')
    search_fields = ('name', 'url')

@admin.register(URLStatus)
class URLStatusAdmin(admin.ModelAdmin):
    list_display = ('url', 'timestamp', 'is_up', 'status_code')
    list_filter = ('is_up', 'timestamp')
    search_fields = ('url__name', 'error_message')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('url', 'user', 'method', 'is_active')
    list_filter = ('method', 'is_active')
    search_fields = ('url__name', 'destination')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message',)

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'visitor_id', 'device_type', 'country', 'timestamp')
    list_filter = ('device_type', 'country', 'timestamp')
    search_fields = ('page_url', 'visitor_id', 'session_id')
    readonly_fields = ('timestamp',)

@admin.register(ClickHeatmap)
class ClickHeatmapAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'element_tag', 'device_type', 'timestamp')
    list_filter = ('device_type', 'element_tag', 'timestamp')
    search_fields = ('page_url', 'element_id', 'element_class')
    readonly_fields = ('timestamp',)

@admin.register(MouseMovement)
class MouseMovementAdmin(admin.ModelAdmin):
    list_display = ('movement_type', 'page_url', 'click_count', 'timestamp')
    list_filter = ('movement_type', 'timestamp')
    search_fields = ('page_url', 'session_id')
    readonly_fields = ('timestamp',)

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'largest_contentful_paint', 'first_input_delay', 'cumulative_layout_shift', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('page_url', 'session_id')
    readonly_fields = ('timestamp',)
