from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum, F, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta
from functools import wraps
from .models import (
    MonitoredURL, PageView, ClickHeatmap, ScrollHeatmap,
    MouseMovement, SessionRecording, PerformanceMetric
)
import json
import logging

logger = logging.getLogger(__name__)


def handle_analytics_errors(view_func):
    """Decorator to handle errors in analytics views gracefully"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {view_func.__name__}: {str(e)}", exc_info=True)
            
            # Get template name from view function
            template_map = {
                'analytics_overview': 'analytics/overview.html',
                'heatmap_view': 'analytics/heatmap.html',
                'geolocation_view': 'analytics/geolocation.html',
                'performance_view': 'analytics/performance.html',
                'scroll_depth_view': 'analytics/scroll_depth.html',
                'session_recordings_view': 'analytics/sessions.html',
            }
            
            template = template_map.get(view_func.__name__, 'analytics/overview.html')
            
            context = {
                'error_message': f'Unable to load analytics data: {str(e)}',
                'days': 7,
            }
            return render(request, template, context)
    return wrapper


@login_required
def analytics_overview(request):
    """Main analytics dashboard showing overview of all metrics"""
    try:
        # Get date range (last 7 days by default)
        days = int(request.GET.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        logger.info(f"Loading analytics overview for {days} days starting from {start_date}")
        
        # Get total metrics
        total_pageviews = PageView.objects.filter(timestamp__gte=start_date).count()
        unique_visitors = PageView.objects.filter(timestamp__gte=start_date).values('visitor_id').distinct().count()
        avg_time_on_page = PageView.objects.filter(
            timestamp__gte=start_date,
            time_on_page__gt=0
        ).aggregate(Avg('time_on_page'))['time_on_page__avg'] or 0
        
        # Get bounce rate (sessions with only 1 pageview)
        total_sessions = PageView.objects.filter(timestamp__gte=start_date).values('session_id').distinct().count()
        single_page_sessions = PageView.objects.filter(timestamp__gte=start_date).values('session_id').annotate(
            page_count=Count('id')
        ).filter(page_count=1).count()
        bounce_rate = (single_page_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Get pageviews by day
        pageviews_by_day = PageView.objects.filter(
            timestamp__gte=start_date
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('id'),
            unique=Count('visitor_id', distinct=True)
        ).order_by('date')
        
        # Get top pages
        top_pages = PageView.objects.filter(
            timestamp__gte=start_date
        ).values('page_url').annotate(
            views=Count('id'),
            unique_views=Count('visitor_id', distinct=True),
            avg_time=Avg('time_on_page'),
            avg_scroll=Avg('scroll_depth')
        ).order_by('-views')[:10]
        
        # Get device breakdown
        device_breakdown = PageView.objects.filter(
            timestamp__gte=start_date
        ).values('device_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get browser breakdown
        browser_breakdown = PageView.objects.filter(
            timestamp__gte=start_date
        ).values('browser').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Get top countries
        top_countries = PageView.objects.filter(
            timestamp__gte=start_date,
            country__isnull=False
        ).exclude(country='').values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        context = {
            'days': days,
            'total_pageviews': total_pageviews,
            'unique_visitors': unique_visitors,
            'avg_time_on_page': round(avg_time_on_page, 2),
            'bounce_rate': round(bounce_rate, 2),
            'pageviews_by_day': json.dumps(list(pageviews_by_day), default=str),
            'top_pages': list(top_pages),
            'device_breakdown': json.dumps(list(device_breakdown)),
            'browser_breakdown': list(browser_breakdown),
            'top_countries': list(top_countries),
        }
        
        logger.info(f"Analytics overview loaded successfully: {total_pageviews} pageviews, {unique_visitors} unique visitors")
        return render(request, 'analytics/overview.html', context)
        
    except Exception as e:
        logger.error(f"Error loading analytics overview: {str(e)}", exc_info=True)
        
        # Return empty context to prevent 500 error
        context = {
            'days': 7,
            'total_pageviews': 0,
            'unique_visitors': 0,
            'avg_time_on_page': 0,
            'bounce_rate': 0,
            'pageviews_by_day': json.dumps([]),
            'top_pages': [],
            'device_breakdown': json.dumps([]),
            'browser_breakdown': [],
            'top_countries': [],
            'error_message': 'Unable to load analytics data. Please try again later.'
        }
        return render(request, 'analytics/overview.html', context)


@login_required
@handle_analytics_errors
def heatmap_view(request, url_id=None):
    """Heatmap visualization showing click patterns"""
    # Get page URL filter
    page_url = request.GET.get('page_url', '')
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get click data
    clicks_query = ClickHeatmap.objects.filter(timestamp__gte=start_date)
    
    if page_url:
        clicks_query = clicks_query.filter(page_url=page_url)
    elif url_id:
        clicks_query = clicks_query.filter(url_id=url_id)
    
    # Get all pages that have click data
    pages_with_clicks = ClickHeatmap.objects.filter(
        timestamp__gte=start_date
    ).values('page_url').annotate(
        click_count=Count('id')
    ).order_by('-click_count')[:20]
    
    # Get click heatmap data
    click_data = clicks_query.values(
        'x_position', 'y_position', 'viewport_width', 'viewport_height',
        'element_tag', 'element_id', 'element_class'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get rage clicks
    rage_clicks = MouseMovement.objects.filter(
        timestamp__gte=start_date,
        movement_type='rage_click'
    )
    
    if page_url:
        rage_clicks = rage_clicks.filter(page_url=page_url)
    
    rage_click_data = rage_clicks.values(
        'x_position', 'y_position', 'click_count'
    ).annotate(
        occurrences=Count('id')
    ).order_by('-occurrences')
    
    # Get dead clicks
    dead_clicks = MouseMovement.objects.filter(
        timestamp__gte=start_date,
        movement_type='dead_click'
    )
    
    if page_url:
        dead_clicks = dead_clicks.filter(page_url=page_url)
    
    dead_click_data = dead_clicks.values(
        'x_position', 'y_position', 'element_selector'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'page_url': page_url,
        'days': days,
        'pages_with_clicks': list(pages_with_clicks),
        'click_data': json.dumps(list(click_data), default=str),
        'rage_click_data': list(rage_click_data),
        'dead_click_data': list(dead_click_data),
        'total_clicks': clicks_query.count(),
        'total_rage_clicks': rage_clicks.count(),
        'total_dead_clicks': dead_clicks.count(),
    }
    
    return render(request, 'analytics/heatmap.html', context)


@login_required
@handle_analytics_errors
def geolocation_view(request):
    """Geographic distribution of visitors"""
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get visitor locations
    visitor_locations = PageView.objects.filter(
        timestamp__gte=start_date,
        latitude__isnull=False,
        longitude__isnull=False
    ).values(
        'latitude', 'longitude', 'city', 'country'
    ).annotate(
        visits=Count('id')
    ).order_by('-visits')
    
    # Get country statistics
    country_stats = PageView.objects.filter(
        timestamp__gte=start_date,
        country__isnull=False
    ).exclude(country='').values('country', 'country_code').annotate(
        visits=Count('id'),
        unique_visitors=Count('visitor_id', distinct=True),
        avg_time=Avg('time_on_page'),
        avg_scroll=Avg('scroll_depth')
    ).order_by('-visits')[:20]
    
    # Get city statistics
    city_stats = PageView.objects.filter(
        timestamp__gte=start_date,
        city__isnull=False
    ).exclude(city='').values('city', 'country').annotate(
        visits=Count('id'),
        unique_visitors=Count('visitor_id', distinct=True)
    ).order_by('-visits')[:15]
    
    context = {
        'days': days,
        'visitor_locations': list(visitor_locations),
        'country_stats': list(country_stats),
        'city_stats': list(city_stats),
        'total_locations': visitor_locations.count(),
    }
    
    return render(request, 'analytics/geolocation.html', context)


@login_required
@handle_analytics_errors
def performance_view(request):
    """Performance metrics dashboard showing Web Vitals"""
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get average metrics
    avg_metrics = PerformanceMetric.objects.filter(
        timestamp__gte=start_date
    ).aggregate(
        avg_fcp=Avg('first_contentful_paint'),
        avg_lcp=Avg('largest_contentful_paint'),
        avg_fid=Avg('first_input_delay'),
        avg_cls=Avg('cumulative_layout_shift'),
        avg_tti=Avg('time_to_interactive'),
        avg_dom_load=Avg('dom_load_time'),
        avg_page_load=Avg('page_load_time')
    )
    
    # Get metrics over time
    metrics_over_time = PerformanceMetric.objects.filter(
        timestamp__gte=start_date
    ).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        avg_fcp=Avg('first_contentful_paint'),
        avg_lcp=Avg('largest_contentful_paint'),
        avg_fid=Avg('first_input_delay'),
        avg_cls=Avg('cumulative_layout_shift'),
        count=Count('id')
    ).order_by('date')
    
    # Get performance by page
    performance_by_page = PerformanceMetric.objects.filter(
        timestamp__gte=start_date
    ).values('page_url').annotate(
        samples=Count('id'),
        avg_fcp=Avg('first_contentful_paint'),
        avg_lcp=Avg('largest_contentful_paint'),
        avg_fid=Avg('first_input_delay'),
        avg_cls=Avg('cumulative_layout_shift'),
        avg_page_load=Avg('page_load_time')
    ).order_by('-samples')[:10]
    
    # Get performance by device
    performance_by_device = PageView.objects.filter(
        timestamp__gte=start_date
    ).values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Calculate scores (Google's thresholds)
    def calculate_score(metrics):
        scores = {
            'fcp': 'good' if (metrics.get('avg_fcp') or 0) < 1800 else ('needs_improvement' if (metrics.get('avg_fcp') or 0) < 3000 else 'poor'),
            'lcp': 'good' if (metrics.get('avg_lcp') or 0) < 2500 else ('needs_improvement' if (metrics.get('avg_lcp') or 0) < 4000 else 'poor'),
            'fid': 'good' if (metrics.get('avg_fid') or 0) < 100 else ('needs_improvement' if (metrics.get('avg_fid') or 0) < 300 else 'poor'),
            'cls': 'good' if (metrics.get('avg_cls') or 0) < 0.1 else ('needs_improvement' if (metrics.get('avg_cls') or 0) < 0.25 else 'poor'),
        }
        return scores
    
    context = {
        'days': days,
        'avg_metrics': avg_metrics,
        'scores': calculate_score(avg_metrics),
        'metrics_over_time': json.dumps(list(metrics_over_time), default=str),
        'performance_by_page': list(performance_by_page),
        'performance_by_device': list(performance_by_device),
    }
    
    return render(request, 'analytics/performance.html', context)


@login_required
@handle_analytics_errors
def scroll_depth_view(request):
    """Scroll depth analysis"""
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get scroll depth distribution
    scroll_heatmaps = ScrollHeatmap.objects.filter(
        date__gte=start_date.date()
    ).order_by('-date')
    
    # Get average scroll depth by page
    scroll_by_page = PageView.objects.filter(
        timestamp__gte=start_date,
        scroll_depth__gt=0
    ).values('page_url').annotate(
        avg_scroll=Avg('scroll_depth'),
        views=Count('id'),
        scrolled_to_bottom=Count('id', filter=Q(scroll_depth__gte=90))
    ).order_by('-views')[:15]
    
    context = {
        'days': days,
        'scroll_heatmaps': scroll_heatmaps,
        'scroll_by_page': list(scroll_by_page),
    }
    
    return render(request, 'analytics/scroll_depth.html', context)


@login_required
@handle_analytics_errors
def session_recordings_view(request):
    """Session recordings list and player"""
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get sessions
    sessions = SessionRecording.objects.filter(
        start_time__gte=start_date
    ).order_by('-start_time')[:50]
    
    # Get session details if session_id is provided
    session_id = request.GET.get('session_id')
    session_details = None
    
    if session_id:
        try:
            session_details = SessionRecording.objects.get(session_id=session_id)
            # Get all pageviews for this session
            session_pageviews = PageView.objects.filter(
                session_id=session_id
            ).order_by('timestamp')
            session_details.pageviews = session_pageviews
        except SessionRecording.DoesNotExist:
            pass
    
    context = {
        'days': days,
        'sessions': sessions,
        'session_details': session_details,
    }
    
    return render(request, 'analytics/sessions.html', context)
