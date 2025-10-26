"""
URL configuration for monitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from . import analytics_api
from . import analytics_views
from . import external_tracking

app_name = 'monitor'

urlpatterns = [
     # Health Check
    path('health/', views.health_check, name='health_check'),
    
     # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # URLs
    path('urls/', views.url_list, name='url_list'),
    path('urls/add/', views.add_url, name='add_url'),
    path('urls/<uuid:url_id>/', views.url_detail, name='url_detail'),
    path('urls/<uuid:url_id>/edit/', views.edit_url, name='edit_url'),
    path('urls/<uuid:url_id>/delete/', views.delete_url, name='delete_url'),
    path('urls/<uuid:url_id>/check/', views.check_now, name='check_now'),
    
    # API Endpoints
    path('api/urls/<uuid:url_id>/status/', views.get_url_status, name='get_url_status'),
    path('api/urls/<uuid:url_id>/chart/', views.get_uptime_chart_data, name='get_uptime_chart_data'),
    
    # External URL Tracking (for monitored websites) - Primary tracking system
    path('tracking/<uuid:url_id>/script.js', external_tracking.get_tracking_script, name='tracking_script'),
    path('api/track/<uuid:url_id>/', external_tracking.track_external_url, name='track_external_url'),
    path('tracking/<uuid:url_id>/instructions/', external_tracking.get_tracking_instructions, name='tracking_instructions'),
    
    # Alerts
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/add/', views.add_alert, name='add_alert'),
    path('alerts/add/<uuid:url_id>/', views.add_alert, name='add_alert_for_url'),
    path('alerts/<int:alert_id>/delete/', views.delete_alert, name='delete_alert'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),

    # Analytics Dashboard
    path('analytics/', analytics_views.analytics_overview, name='analytics_overview'),
    path('analytics/<uuid:url_id>/', analytics_views.analytics_overview, name='analytics_overview_url'),
    path('analytics/heatmap/', analytics_views.heatmap_view, name='analytics_heatmap'),
    path('analytics/heatmap/<uuid:url_id>/', analytics_views.heatmap_view, name='analytics_heatmap_url'),
    path('analytics/geolocation/', analytics_views.geolocation_view, name='analytics_geolocation'),
    path('analytics/geolocation/<uuid:url_id>/', analytics_views.geolocation_view, name='analytics_geolocation_url'),
    path('analytics/performance/', analytics_views.performance_view, name='analytics_performance'),
    path('analytics/performance/<uuid:url_id>/', analytics_views.performance_view, name='analytics_performance_url'),
    path('analytics/scroll/', analytics_views.scroll_depth_view, name='analytics_scroll'),
    path('analytics/scroll/<uuid:url_id>/', analytics_views.scroll_depth_view, name='analytics_scroll_url'),
    
    # Export
    path('urls/<uuid:url_id>/export/<str:format>/', views.export_url_data, name='export_url_data'),
]
