from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
from .models import (
    MonitoredURL, PageView, ClickHeatmap,
    MouseMovement, PerformanceMetric
)
from user_agents import parse
import requests


def get_geolocation(ip_address):
    """Get geolocation data from IP address using ipapi.co"""
    if not ip_address or ip_address in ['127.0.0.1', 'localhost']:
        return {}
    
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                'country': data.get('country_name', ''),
                'country_code': data.get('country_code', ''),
                'city': data.get('city', ''),
                'region': data.get('region', ''),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone', ''),
            }
    except Exception as e:
        print(f"Geolocation lookup failed: {e}")
    
    return {}


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_POST
def track_analytics(request):
    """
    Main endpoint for receiving analytics events from the tracking script
    """
    try:
        data = json.loads(request.body)
        events = data.get('events', [])
        
        if not events:
            return JsonResponse({'status': 'error', 'message': 'No events provided'}, status=400)
        
        # Get IP and user agent
        ip_address = get_client_ip(request)
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        
        # Get geolocation (cache this per IP to avoid too many API calls)
        geo_data = get_geolocation(ip_address)
        
        # Parse user agent
        user_agent = parse(user_agent_string)
        device_type = 'mobile' if user_agent.is_mobile else ('tablet' if user_agent.is_tablet else 'desktop')
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        os = f"{user_agent.os.family} {user_agent.os.version_string}"
        
        # Process each event
        for event in events:
            event_type = event.get('type')
            
            try:
                # Get or create the monitored URL (you might want to match by domain)
                # For now, we'll skip if we can't find a matching URL
                # In production, you'd want better URL matching logic
                
                if event_type == 'pageview':
                    process_pageview(event, ip_address, geo_data, device_type, browser, os)
                
                elif event_type == 'click':
                    process_click(event, device_type)
                
                elif event_type == 'scroll':
                    # Scroll events are now handled by external_tracking.py
                    pass
                
                elif event_type in ['rage_click', 'dead_click', 'error_click', 'hover']:
                    process_mouse_movement(event)
                
                elif event_type == 'performance':
                    process_performance(event)
                
                elif event_type == 'page_leave':
                    process_page_leave(event)
                
            except Exception as e:
                print(f"Error processing event {event_type}: {e}")
                continue
        
        return JsonResponse({'status': 'success', 'processed': len(events)})
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Analytics tracking error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def process_pageview(event, ip_address, geo_data, device_type, browser, os):
    """Process pageview event"""
    # Try to find matching MonitoredURL
    # This is a simplified version - you'd want more sophisticated matching
    page_url = event.get('page_url', '')
    
    # For now, create pageview without URL reference (you can improve this)
    # Or you could add a field to MonitoredURL to track which pages to monitor
    
    PageView.objects.create(
        url_id=None,  # Set this based on your URL matching logic
        session_id=event.get('session_id'),
        visitor_id=event.get('visitor_id'),
        page_url=page_url,
        page_title=event.get('page_title', ''),
        referrer=event.get('referrer', ''),
        user_agent=event.get('user_agent', ''),
        device_type=device_type,
        browser=browser,
        os=os,
        screen_resolution=event.get('screen_resolution', ''),
        ip_address=ip_address,
        **geo_data
    )


def process_click(event, device_type):
    """Process click event"""
    ClickHeatmap.objects.create(
        url_id=None,  # Set based on URL matching
        page_url=event.get('page_url'),
        x_position=event.get('x_position'),
        y_position=event.get('y_position'),
        viewport_width=event.get('viewport_width'),
        viewport_height=event.get('viewport_height'),
        element_tag=event.get('element_tag', ''),
        element_id=event.get('element_id', ''),
        element_class=event.get('element_class', ''),
        element_text=event.get('element_text', ''),
        session_id=event.get('session_id'),
        device_type=device_type
    )


# Removed process_scroll() - now handled by external_tracking.py which updates PageView.scroll_depth


def process_mouse_movement(event):
    """Process rage clicks, dead clicks, etc."""
    MouseMovement.objects.create(
        url_id=None,  # Set based on URL matching
        session_id=event.get('session_id'),
        page_url=event.get('page_url'),
        movement_type=event.get('type'),
        x_position=event.get('x_position', 0),
        y_position=event.get('y_position', 0),
        click_count=event.get('click_count', 1),
        element_selector=event.get('element_selector', '')
    )


def process_performance(event):
    """Process performance metrics"""
    PerformanceMetric.objects.create(
        url_id=None,  # Set based on URL matching
        page_url=event.get('page_url'),
        session_id=event.get('session_id'),
        first_contentful_paint=event.get('first_contentful_paint'),
        largest_contentful_paint=event.get('largest_contentful_paint'),
        first_input_delay=event.get('first_input_delay'),
        cumulative_layout_shift=event.get('cumulative_layout_shift'),
        time_to_interactive=event.get('time_to_interactive'),
        dom_load_time=event.get('dom_load_time'),
        page_load_time=event.get('page_load_time'),
        resource_load_time=event.get('resource_load_time'),
        connection_type=event.get('connection_type', ''),
        effective_bandwidth=event.get('effective_bandwidth')
    )


def process_page_leave(event):
    """Process page leave event - update PageView with final metrics"""
    try:
        # Find the pageview to update
        pageview = PageView.objects.filter(
            session_id=event.get('session_id'),
            visitor_id=event.get('visitor_id'),
            page_url=event.get('page_url')
        ).latest('timestamp')
        
        pageview.time_on_page = event.get('time_on_page', 0)
        pageview.scroll_depth = event.get('scroll_depth', 0)
        pageview.scroll_events = event.get('scroll_events', [])
        pageview.click_count = event.get('click_count', 0)
        pageview.save()
        
    except PageView.DoesNotExist:
        pass
