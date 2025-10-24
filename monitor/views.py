from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    MonitoredURL, URLStatus, Alert, Notification,
    TrafficMetric, UserFlow, Engagement,
    URLGroup, StatusPage, StatusPageURL
)
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
import csv

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
    chart_labels = []
    chart_uptime = []
    chart_response_times = []
    
    for url in urls:
        statuses = url.statuses.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).order_by('timestamp')
        
        if statuses.exists():
            up_count = statuses.filter(is_up=True).count()
            uptime_percent = (up_count / statuses.count()) * 100
            avg_response = statuses.aggregate(avg=Avg('response_time'))['avg'] or 0
            
            uptime_data.append({
                'url': url,
                'uptime': round(uptime_percent, 2),
                'avg_response': round(avg_response, 2) if avg_response else 0
            })
    
    # Prepare chart data for the last 7 days
    if urls.exists():
        # Get daily aggregated data for charts
        from datetime import date
        today = timezone.now().date()
        
        for i in range(6, -1, -1):  # Last 7 days
            day = today - timedelta(days=i)
            day_start = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            
            # Get statuses for this day across all URLs
            day_statuses = URLStatus.objects.filter(
                url__user=request.user,
                url__is_active=True,
                timestamp__gte=day_start,
                timestamp__lt=day_end
            )
            
            if day_statuses.exists():
                # Calculate uptime percentage for this day
                up_count = day_statuses.filter(is_up=True).count()
                total_count = day_statuses.count()
                uptime_pct = round((up_count / total_count) * 100, 2) if total_count > 0 else 0
                
                # Calculate average response time for this day
                avg_response = day_statuses.aggregate(avg=Avg('response_time'))['avg'] or 0
                avg_response = round(avg_response, 2) if avg_response else 0
                
                chart_labels.append(day.strftime('%b %d'))
                chart_uptime.append(uptime_pct)
                chart_response_times.append(avg_response)
            else:
                chart_labels.append(day.strftime('%b %d'))
                chart_uptime.append(0)
                chart_response_times.append(0)
    
    # Convert to JSON for JavaScript
    urls_json = json.dumps(chart_labels)
    uptime_json = json.dumps(chart_uptime)
    response_times_json = json.dumps(chart_response_times)
    
    context = {
        'stats': stats,
        'notifications': notifications,
        'uptime_data': uptime_data,
        'urls': urls,
        'urls_json': urls_json,
        'uptime_json': uptime_json,
        'response_times_json': response_times_json,
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
        form = URLForm(request.user, request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.save()
            messages.success(request, 'URL added successfully!')
            return redirect('monitor:url_list')
    else:
        form = URLForm(request.user)
    return render(request, 'url_form.html', {'form': form, 'action': 'Add'})

@login_required
@require_http_methods(['GET', 'POST'])
def edit_url(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    if request.method == 'POST':
        form = URLForm(request.user, request.POST, instance=url)
        if form.is_valid():
            form.save()
            messages.success(request, 'URL updated successfully!')
            return redirect('monitor:url_detail', url_id=url.id)
    else:
        form = URLForm(request.user, instance=url)
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

@login_required
def analytics_test(request):
    """Test page for analytics tracking"""
    return render(request, 'analytics_test.html')

@login_required
def traffic_dashboard(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    metrics = TrafficMetric.objects.filter(url=url).order_by('-timestamp')[:24]
    
    # Process data for charts
    time_labels = [m.timestamp.strftime('%H:%M') for m in reversed(metrics)]
    request_data = [m.requests for m in reversed(metrics)]
    bandwidth_data = [m.bandwidth for m in reversed(metrics)]
    
    return render(request, 'traffic_dashboard.html', {
        'url': url,
        'time_labels': json.dumps(time_labels),
        'request_data': json.dumps(request_data),
        'bandwidth_data': json.dumps(bandwidth_data)
    })

@login_required
def user_flows(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    flows = UserFlow.objects.filter(url=url).order_by('-timestamp_end')[:100]
    
    # Process for Sankey diagram
    path_links = {}
    for flow in flows:
        path = flow.path_sequence
        for i in range(len(path)-1):
            key = f"{path[i]}→{path[i+1]}"
            path_links[key] = path_links.get(key, 0) + 1
    
    return render(request, 'user_flows.html', {
        'url': url,
        'flows': flows,
        'path_links': path_links
    })

def engagement_metrics(request, url_id):
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    metrics = Engagement.objects.filter(url=url).order_by('-timestamp')[:1000]
    
    # Calculate aggregates
    avg_duration = metrics.aggregate(avg=Avg('duration'))['avg']
    bounce_rate = metrics.filter(interactions__lt=2).count() / metrics.count() if metrics.count() > 0 else 0
    
    return render(request, 'engagement.html', {
        'url': url,
        'metrics': metrics,
        'avg_duration': avg_duration,
        'bounce_rate': bounce_rate
    })

# ==================== EXPORT VIEWS ====================

@login_required
def export_url_data(request, url_id, format='csv'):
    """Export URL monitoring data to CSV or JSON"""
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    statuses = url.statuses.all()[:1000]  # Last 1000 records
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{url.name}_data.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Status Code', 'Response Time (ms)', 'Is Up', 'Error Message'])
        
        for status in statuses:
            writer.writerow([
                status.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                status.status_code,
                f"{status.response_time:.2f}",
                'Yes' if status.is_up else 'No',
                status.error_message or ''
            ])
        
        return response
    
    elif format == 'json':
        data = {
            'url': {
                'name': url.name,
                'url': url.url,
                'frequency': url.frequency,
                'expected_status': url.expected_status
            },
            'statuses': [
                {
                    'timestamp': status.timestamp.isoformat(),
                    'status_code': status.status_code,
                    'response_time': status.response_time,
                    'is_up': status.is_up,
                    'error_message': status.error_message
                }
                for status in statuses
            ]
        }
        response = JsonResponse(data)
        response['Content-Disposition'] = f'attachment; filename="{url.name}_data.json"'
        return response
    
    return HttpResponse('Invalid format', status=400)

# ==================== GROUP MANAGEMENT ====================

@login_required
def group_list(request):
    """List all URL groups"""
    groups = URLGroup.objects.filter(user=request.user)
    return render(request, 'group_list.html', {'groups': groups})

@login_required
def group_create(request):
    """Create a new URL group"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        color = request.POST.get('color', '#3B82F6')
        
        URLGroup.objects.create(
            user=request.user,
            name=name,
            description=description,
            color=color
        )
        messages.success(request, f'Group "{name}" created successfully!')
        return redirect('monitor:group_list')
    
    return render(request, 'group_form.html', {'action': 'Create'})

@login_required
def group_edit(request, group_id):
    """Edit an existing group"""
    group = get_object_or_404(URLGroup, id=group_id, user=request.user)
    
    if request.method == 'POST':
        group.name = request.POST.get('name')
        group.description = request.POST.get('description', '')
        group.color = request.POST.get('color', '#3B82F6')
        group.save()
        messages.success(request, 'Group updated successfully!')
        return redirect('monitor:group_list')
    
    return render(request, 'group_form.html', {'group': group, 'action': 'Edit'})

@login_required
def group_delete(request, group_id):
    """Delete a group"""
    group = get_object_or_404(URLGroup, id=group_id, user=request.user)
    group_name = group.name
    group.delete()
    messages.success(request, f'Group "{group_name}" deleted successfully!')
    return redirect('monitor:group_list')

# ==================== STATUS PAGE VIEWS ====================

@login_required
def status_page_list(request):
    """List all status pages"""
    pages = StatusPage.objects.filter(user=request.user)
    return render(request, 'status_page_list.html', {'pages': pages})

@login_required
def status_page_create(request):
    """Create a new status page"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        slug = request.POST.get('slug')
        
        page = StatusPage.objects.create(
            user=request.user,
            title=title,
            description=description,
            slug=slug
        )
        messages.success(request, f'Status page "{title}" created successfully!')
        return redirect('monitor:status_page_edit', page_id=page.id)
    
    return render(request, 'status_page_form.html', {'action': 'Create'})

@login_required
def status_page_edit(request, page_id):
    """Edit a status page"""
    page = get_object_or_404(StatusPage, id=page_id, user=request.user)
    
    if request.method == 'POST':
        page.title = request.POST.get('title')
        page.description = request.POST.get('description', '')
        page.is_public = request.POST.get('is_public') == 'on'
        page.show_response_time = request.POST.get('show_response_time') == 'on'
        page.show_uptime_percentage = request.POST.get('show_uptime_percentage') == 'on'
        page.theme_color = request.POST.get('theme_color', '#3B82F6')
        page.save()
        messages.success(request, 'Status page updated successfully!')
        return redirect('monitor:status_page_list')
    
    # Get URLs on this page
    page_urls = StatusPageURL.objects.filter(status_page=page).select_related('url')
    # Get available URLs not on this page
    available_urls = MonitoredURL.objects.filter(user=request.user, is_active=True).exclude(
        id__in=page_urls.values_list('url_id', flat=True)
    )
    
    return render(request, 'status_page_form.html', {
        'page': page,
        'page_urls': page_urls,
        'available_urls': available_urls,
        'action': 'Edit'
    })

@login_required
def status_page_delete(request, page_id):
    """Delete a status page"""
    page = get_object_or_404(StatusPage, id=page_id, user=request.user)
    page_title = page.title
    page.delete()
    messages.success(request, f'Status page "{page_title}" deleted successfully!')
    return redirect('monitor:status_page_list')

@login_required
def status_page_add_url(request, page_id, url_id):
    """Add a URL to a status page"""
    page = get_object_or_404(StatusPage, id=page_id, user=request.user)
    url = get_object_or_404(MonitoredURL, id=url_id, user=request.user)
    
    StatusPageURL.objects.get_or_create(
        status_page=page,
        url=url,
        defaults={'display_name': url.name}
    )
    messages.success(request, f'"{url.name}" added to status page!')
    return redirect('monitor:status_page_edit', page_id=page.id)

@login_required
def status_page_remove_url(request, page_id, url_id):
    """Remove a URL from a status page"""
    page = get_object_or_404(StatusPage, id=page_id, user=request.user)
    StatusPageURL.objects.filter(status_page=page, url_id=url_id).delete()
    messages.success(request, 'URL removed from status page!')
    return redirect('monitor:status_page_edit', page_id=page.id)

def public_status_page(request, slug):
    """Public view of a status page"""
    page = get_object_or_404(StatusPage, slug=slug)
    
    if not page.is_public:
        raise Http404("Status page not found")
    
    # Get URLs on this page with their latest status
    page_urls = StatusPageURL.objects.filter(status_page=page).select_related('url').order_by('order')
    
    url_data = []
    for page_url in page_urls:
        url = page_url.url
        latest_status = url.statuses.first()
        
        # Calculate uptime for last 24h
        day_ago = timezone.now() - timedelta(hours=24)
        statuses_24h = url.statuses.filter(timestamp__gte=day_ago)
        uptime_24h = 0
        if statuses_24h.exists():
            up_count = statuses_24h.filter(is_up=True).count()
            uptime_24h = (up_count / statuses_24h.count()) * 100
        
        url_data.append({
            'name': page_url.display_name or url.name,
            'latest_status': latest_status,
            'uptime_24h': round(uptime_24h, 2) if uptime_24h else 0,
            'avg_response': round(statuses_24h.aggregate(avg=Avg('response_time'))['avg'] or 0, 2) if statuses_24h.exists() else 0
        })
    
    return render(request, 'public_status_page.html', {
        'page': page,
        'url_data': url_data
    })
