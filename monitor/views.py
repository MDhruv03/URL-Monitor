from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import MonitoredURL, URLStatus, Alert, Notification
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    URLForm,
    AlertForm,
    NotificationSettingsForm
)
from django_tables2 import RequestConfig
from .tables import URLTable, StatusTable, AlertTable, NotificationTable
import json

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('monitor:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('monitor:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid login. Please check your credentials.')
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('monitor:login')

@login_required
def dashboard(request):
    # Get user's URLs
    urls = MonitoredURL.objects.filter(user=request.user, is_active=True)
    
    # Calculate stats
    stats = {
        'total_urls': urls.count(),
        'up_urls': 0,
        'down_urls': 0,
        'avg_response_time': 0,
    }
    
    if urls.exists():
        # Get latest status for each URL
        latest_statuses = []
        for url in urls:
            latest = url.statuses.first()
            if latest:
                latest_statuses.append(latest)
                if latest.is_up:
                    stats['up_urls'] += 1
                else:
                    stats['down_urls'] += 1
        
        # Calculate average response time
        if latest_statuses:
            stats['avg_response_time'] = sum(
                s.response_time for s in latest_statuses if s.response_time > 0
            ) / len(latest_statuses)
    
    # Get recent notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get uptime stats for the last 7 days
    uptime_data = []
    for url in urls:
        statuses = url.statuses.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).order_by('timestamp')
        
        if statuses.exists():
            up_count = statuses.filter(is_up=True).count()
            uptime_percent = (up_count / statuses.count()) * 100
            uptime_data.append({
                'url': url,
                'uptime': round(uptime_percent, 2),
                'avg_response': round(statuses.aggregate(avg=Avg('response_time'))['avg'], 2)
            })
    
    context = {
        'stats': stats,
        'notifications': notifications,
        'uptime_data': uptime_data,
        'urls': urls,
    }
    return render(request, 'dashboard.html', context)

@login_required
def url_list(request):
    table = URLTable(MonitoredURL.objects.filter(user=request.user))
    RequestConfig(request, paginate={'per_page': 10}).configure(table)
    return render(request, 'url_list.html', {'table': table})

@login_required
def url_detail(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    status_table = StatusTable(url.statuses.all())
    RequestConfig(request, paginate={'per_page': 10}).configure(status_table)
    
    # Calculate uptime percentages
    now = timezone.now()
    time_ranges = {
        '24h': now - timedelta(hours=24),
        '7d': now - timedelta(days=7),
        '30d': now - timedelta(days=30),
    }
    
    uptime_stats = {}
    for label, start_time in time_ranges.items():
        statuses = url.statuses.filter(timestamp__gte=start_time)
        if statuses.exists():
            up_count = statuses.filter(is_up=True).count()
            uptime_stats[label] = round((up_count / statuses.count()) * 100, 2)
        else:
            uptime_stats[label] = 0.0
    
    # Response time stats
    response_stats = {
        '24h': url.statuses.filter(
            timestamp__gte=now - timedelta(hours=24)
        ).aggregate(avg=Avg('response_time'))['avg'] or 0,
        '7d': url.statuses.filter(
            timestamp__gte=now - timedelta(days=7)
        ).aggregate(avg=Avg('response_time'))['avg'] or 0,
    }
    
    context = {
        'url': url,
        'status_table': status_table,
        'uptime_stats': uptime_stats,
        'response_stats': response_stats,
    }
    return render(request, 'url_detail.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def add_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.save()
            messages.success(request, 'URL added successfully!')
            return redirect('monitor:url_list')
    else:
        form = URLForm()
    return render(request, 'url_form.html', {'form': form, 'action': 'Add'})

@login_required
@require_http_methods(['GET', 'POST'])
def edit_url(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    if request.method == 'POST':
        form = URLForm(request.POST, instance=url)
        if form.is_valid():
            form.save()
            messages.success(request, 'URL updated successfully!')
            return redirect('monitor:url_detail', url_id=url.id)
    else:
        form = URLForm(instance=url)
    return render(request, 'url_form.html', {'form': form, 'action': 'Edit'})

@login_required
@require_http_methods(['POST'])
def delete_url(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    url.is_active = False
    url.save()
    messages.success(request, 'URL monitoring stopped successfully!')
    return redirect('monitor:url_list')

@login_required
def check_now(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    from .tasks import check_url_status
    result = check_url_status.delay(str(url.id))
    messages.info(request, 'URL check initiated. Results will appear shortly.')
    return redirect('monitor:url_detail', url_id=url.id)

@login_required
def alert_list(request):
    alerts = Alert.objects.filter(user=request.user)
    table = AlertTable(alerts)
    RequestConfig(request, paginate={'per_page': 10}).configure(table)
    return render(request, 'alert_list.html', {'table': table})

@login_required
def add_alert(request, url_id=None):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user) if url_id else None
    
    if request.method == 'POST':
        form = AlertForm(request.user, request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            if url:
                alert.url = url
            alert.save()
            messages.success(request, 'Alert added successfully!')
            return redirect('monitor:alert_list')
    else:
        initial = {'url': url.id} if url else {}
        form = AlertForm(request.user, initial=initial)
    
    return render(request, 'alert_form.html', {'form': form, 'action': 'Add'})

@login_required
def delete_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    alert.delete()
    messages.success(request, 'Alert deleted successfully!')
    return redirect('monitor:alert_list')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    table = NotificationTable(notifications)
    RequestConfig(request, paginate={'per_page': 20}).configure(table)
    return render(request, 'notifications.html', {'table': table})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def get_url_status(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    latest_status = url.statuses.first()
    
    if latest_status:
        data = {
            'is_up': latest_status.is_up,
            'status_code': latest_status.status_code,
            'response_time': latest_status.response_time,
            'timestamp': latest_status.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'error': latest_status.error_message,
        }
    else:
        data = {'error': 'No status data available'}
    
    return JsonResponse(data)

@login_required
def get_uptime_chart_data(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    
    # Get data for the last 7 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    
    # Group by day and hour
    statuses = url.statuses.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).order_by('timestamp')
    
    # Prepare chart data
    chart_data = {
        'labels': [],
        'up': [],
        'down': [],
        'response_times': []
    }
    
    # Group by hour
    current_hour = start_date.replace(minute=0, second=0, microsecond=0)
    while current_hour <= end_date:
        hour_statuses = statuses.filter(
            timestamp__gte=current_hour,
            timestamp__lt=current_hour + timedelta(hours=1)
        )
        
        if hour_statuses.exists():
            up_count = hour_statuses.filter(is_up=True).count()
            total = hour_statuses.count()
            uptime = (up_count / total) * 100 if total > 0 else 0
            avg_response = hour_statuses.aggregate(avg=Avg('response_time'))['avg'] or 0
            
            chart_data['labels'].append(current_hour.strftime('%Y-%m-%d %H:%M'))
            chart_data['up'].append(uptime)
            chart_data['down'].append(100 - uptime)
            chart_data['response_times'].append(avg_response)
        
        current_hour += timedelta(hours=1)
    
    return JsonResponse(chart_data)

@login_required
def settings_view(request):
    if request.method == 'POST':
        form = NotificationSettingsForm(request.user, request.POST)
        if form.is_valid():
            # Process settings
            pass
    else:
        form = NotificationSettingsForm(request.user)
    
    return render(request, 'settings.html', {'form': form})