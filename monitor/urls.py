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

app_name = 'monitor'

urlpatterns = [
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
]