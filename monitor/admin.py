from django.contrib import admin
from monitor.models import MonitoredURL, URLStatus, Alert, Notification

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