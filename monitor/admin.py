from django.contrib import admin
from monitor.models import (
    MonitoredURL, URLStatus, Alert, Notification,
    URLGroup, StatusPage, StatusPageURL,
    PageView, ClickHeatmap, ScrollHeatmap, MouseMovement,
    SessionRecording, PerformanceMetric, ConversionFunnel
)

@admin.register(URLGroup)
class URLGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'description')

@admin.register(MonitoredURL)
class MonitoredURLAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'user', 'group', 'is_active')
    list_filter = ('is_active', 'user', 'group')
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

@admin.register(StatusPage)
class StatusPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(StatusPageURL)
class StatusPageURLAdmin(admin.ModelAdmin):
    list_display = ('status_page', 'url', 'display_name', 'order')
    list_filter = ('status_page',)
    ordering = ['status_page', 'order']

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

@admin.register(ScrollHeatmap)
class ScrollHeatmapAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'date', 'total_views', 'average_depth')
    list_filter = ('date',)
    search_fields = ('page_url',)

@admin.register(MouseMovement)
class MouseMovementAdmin(admin.ModelAdmin):
    list_display = ('movement_type', 'page_url', 'click_count', 'timestamp')
    list_filter = ('movement_type', 'timestamp')
    search_fields = ('page_url', 'session_id')
    readonly_fields = ('timestamp',)

@admin.register(SessionRecording)
class SessionRecordingAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'start_time', 'end_time', 'pages_visited', 'total_clicks', 'had_rage_clicks')
    list_filter = ('had_rage_clicks', 'start_time')
    search_fields = ('session_id',)
    readonly_fields = ('start_time',)

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'largest_contentful_paint', 'first_input_delay', 'cumulative_layout_shift', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('page_url', 'session_id')
    readonly_fields = ('timestamp',)

@admin.register(ConversionFunnel)
class ConversionFunnelAdmin(admin.ModelAdmin):
    list_display = ('name', 'conversion_rate', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
