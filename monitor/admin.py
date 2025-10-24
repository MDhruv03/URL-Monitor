from django.contrib import admin
from monitor.models import (
    MonitoredURL, URLStatus, Alert, Notification,
    URLGroup, StatusPage, StatusPageURL
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
