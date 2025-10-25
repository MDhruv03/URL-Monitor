"""
External URL Tracking Views
For embedding analytics on monitored websites
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import MonitoredURL, PageView, ClickHeatmap, MouseMovement, PerformanceMetric
from .analytics_api import get_client_ip, get_geolocation
from user_agents import parse
import json


def add_cors_headers(response):
    """Add CORS headers to allow external websites to send tracking data"""
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    response['Access-Control-Max-Age'] = '86400'  # 24 hours
    return response


@require_GET
def get_tracking_script(request, url_id):
    """
    Returns a JavaScript tracking script that can be embedded on monitored websites
    Usage: <script src="/tracking/{url_id}/script.js"></script>
    """
    monitored_url = get_object_or_404(MonitoredURL, id=url_id)
    
    # Generate the tracking script with the URL ID embedded
    script = f"""
(function() {{
    'use strict';
    
    const TRACKING_URL_ID = '{url_id}';
    const API_ENDPOINT = '{request.scheme}://{request.get_host()}/api/track/{url_id}/';
    
    // Generate unique IDs
    const generateId = () => Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    
    const getVisitorId = () => {{
        let visitorId = localStorage.getItem('urlmon_visitor_id');
        if (!visitorId) {{
            visitorId = generateId();
            localStorage.setItem('urlmon_visitor_id', visitorId);
        }}
        return visitorId;
    }};
    
    const getSessionId = () => {{
        let sessionId = sessionStorage.getItem('urlmon_session_id');
        if (!sessionId) {{
            sessionId = generateId();
            sessionStorage.setItem('urlmon_session_id', sessionId);
        }}
        return sessionId;
    }};
    
    class URLMonitorTracker {{
        constructor() {{
            this.visitorId = getVisitorId();
            this.sessionId = getSessionId();
            this.pageLoadTime = Date.now();
            this.eventQueue = [];
            this.maxScrollDepth = 0;
            this.clickCount = 0;
            this.lastClickTime = 0;
            this.lastClickPosition = null;
            
            this.init();
        }}
        
        init() {{
            this.trackPageView();
            this.setupClickTracking();
            this.setupScrollTracking();
            this.trackPerformanceMetrics();
            
            window.addEventListener('beforeunload', () => this.handlePageLeave());
            setInterval(() => this.flush(), 5000);
        }}
        
        trackPageView() {{
            const data = {{
                type: 'pageview',
                session_id: this.sessionId,
                visitor_id: this.visitorId,
                page_url: window.location.pathname,
                page_title: document.title,
                referrer: document.referrer,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                screen_resolution: `${{screen.width}}x${{screen.height}}`,
                viewport_size: `${{window.innerWidth}}x${{window.innerHeight}}`,
                language: navigator.language
            }};
            
            this.sendImmediately(data);
        }}
        
        setupClickTracking() {{
            document.addEventListener('click', (e) => {{
                const now = Date.now();
                const position = {{ x: e.clientX, y: e.clientY }};
                
                this.clickCount++;
                
                // Check for rage click
                if (this.lastClickPosition && 
                    Math.abs(position.x - this.lastClickPosition.x) < 20 &&
                    Math.abs(position.y - this.lastClickPosition.y) < 20 &&
                    now - this.lastClickTime < 1000) {{
                    
                    if (this.clickCount >= 3) {{
                        this.queueEvent({{
                            type: 'rage_click',
                            x_position: position.x,
                            y_position: position.y,
                            click_count: this.clickCount,
                            timestamp: new Date().toISOString()
                        }});
                    }}
                }} else {{
                    this.clickCount = 1;
                }}
                
                this.lastClickTime = now;
                this.lastClickPosition = position;
                
                // Track regular click
                this.queueEvent({{
                    type: 'click',
                    x_position: e.clientX,
                    y_position: e.clientY,
                    viewport_width: window.innerWidth,
                    viewport_height: window.innerHeight,
                    element_tag: e.target.tagName.toLowerCase(),
                    element_id: e.target.id || '',
                    element_class: e.target.className || '',
                    element_text: e.target.textContent?.substring(0, 100) || '',
                    timestamp: new Date().toISOString()
                }});
            }});
        }}
        
        setupScrollTracking() {{
            let scrollTimeout;
            document.addEventListener('scroll', () => {{
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {{
                    const scrollDepth = Math.round(
                        (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
                    );
                    
                    if (scrollDepth > this.maxScrollDepth) {{
                        this.maxScrollDepth = scrollDepth;
                    }}
                    
                    this.queueEvent({{
                        type: 'scroll',
                        scroll_depth: scrollDepth,
                        timestamp: new Date().toISOString()
                    }});
                }}, 150);
            }});
        }}
        
        trackPerformanceMetrics() {{
            if (!window.performance) return;
            
            window.addEventListener('load', () => {{
                setTimeout(() => {{
                    const timing = performance.timing;
                    const data = {{
                        type: 'performance',
                        dom_load_time: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                        page_load_time: timing.loadEventEnd - timing.navigationStart,
                        timestamp: new Date().toISOString()
                    }};
                    
                    // Try to get Web Vitals
                    if (window.PerformanceObserver) {{
                        const paintEntries = performance.getEntriesByType('paint');
                        const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint');
                        if (fcpEntry) data.first_contentful_paint = fcpEntry.startTime;
                    }}
                    
                    this.queueEvent(data);
                }}, 100);
            }});
        }}
        
        handlePageLeave() {{
            const timeOnPage = Math.round((Date.now() - this.pageLoadTime) / 1000);
            this.sendBeacon({{
                type: 'page_leave',
                time_on_page: timeOnPage,
                scroll_depth: this.maxScrollDepth,
                timestamp: new Date().toISOString()
            }});
        }}
        
        queueEvent(data) {{
            this.eventQueue.push(data);
            if (this.eventQueue.length >= 10) {{
                this.flush();
            }}
        }}
        
        flush() {{
            if (this.eventQueue.length === 0) return;
            const events = [...this.eventQueue];
            this.eventQueue = [];
            this.send(events);
        }}
        
        send(events) {{
            fetch(API_ENDPOINT, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ events }}),
                keepalive: true
            }}).catch(() => {{
                this.eventQueue.unshift(...events);
            }});
        }}
        
        sendImmediately(data) {{
            fetch(API_ENDPOINT, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ events: [data] }}),
                keepalive: true
            }}).catch(() => {{}});
        }}
        
        sendBeacon(data) {{
            if (navigator.sendBeacon) {{
                navigator.sendBeacon(API_ENDPOINT, JSON.stringify({{ events: [data] }}));
            }}
        }}
    }}
    
    // Initialize tracker
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', () => new URLMonitorTracker());
    }} else {{
        new URLMonitorTracker();
    }}
}})();
"""
    
    response = HttpResponse(script, content_type='application/javascript')
    return add_cors_headers(response)


@csrf_exempt
def track_external_url(request, url_id):
    """
    Receives tracking data from monitored external websites
    This is called by the embedded tracking script
    Supports CORS for cross-origin requests
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = HttpResponse()
        return add_cors_headers(response)
    
    if request.method != 'POST':
        response = JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        return add_cors_headers(response)
    
    try:
        monitored_url = get_object_or_404(MonitoredURL, id=url_id)
        data = json.loads(request.body)
        events = data.get('events', [])
        
        if not events:
            response = JsonResponse({'status': 'error', 'message': 'No events'}, status=400)
            return add_cors_headers(response)
        
        # Get client info
        ip_address = get_client_ip(request)
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
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
                if event_type == 'pageview':
                    PageView.objects.create(
                        url=monitored_url,
                        session_id=event.get('session_id'),
                        visitor_id=event.get('visitor_id'),
                        page_url=event.get('page_url', ''),
                        page_title=event.get('page_title', ''),
                        referrer=event.get('referrer', ''),
                        user_agent=user_agent_string,
                        device_type=device_type,
                        browser=browser,
                        os=os,
                        screen_resolution=event.get('screen_resolution', ''),
                        ip_address=ip_address,
                        **geo_data
                    )
                
                elif event_type == 'click':
                    ClickHeatmap.objects.create(
                        url=monitored_url,
                        page_url=event.get('page_url', ''),
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
                
                elif event_type == 'rage_click':
                    MouseMovement.objects.create(
                        url=monitored_url,
                        session_id=event.get('session_id'),
                        page_url=event.get('page_url', ''),
                        movement_type='rage_click',
                        x_position=event.get('x_position', 0),
                        y_position=event.get('y_position', 0),
                        click_count=event.get('click_count', 1)
                    )
                
                elif event_type == 'performance':
                    PerformanceMetric.objects.create(
                        url=monitored_url,
                        page_url=event.get('page_url', ''),
                        session_id=event.get('session_id'),
                        first_contentful_paint=event.get('first_contentful_paint'),
                        dom_load_time=event.get('dom_load_time'),
                        page_load_time=event.get('page_load_time')
                    )
                
                elif event_type == 'page_leave':
                    # Update the most recent pageview with final metrics
                    try:
                        pageview = PageView.objects.filter(
                            url=monitored_url,
                            session_id=event.get('session_id'),
                            visitor_id=event.get('visitor_id')
                        ).latest('timestamp')
                        
                        pageview.time_on_page = event.get('time_on_page', 0)
                        pageview.scroll_depth = event.get('scroll_depth', 0)
                        pageview.save()
                    except PageView.DoesNotExist:
                        pass
            
            except Exception as e:
                print(f"Error processing event {event_type}: {e}")
                continue
        
        response = JsonResponse({'status': 'success', 'processed': len(events)})
        return add_cors_headers(response)
    
    except Exception as e:
        print(f"External tracking error: {e}")
        response = JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return add_cors_headers(response)


@require_GET
def get_tracking_instructions(request, url_id):
    """
    Returns instructions for embedding the tracking script
    Shown in the URL detail page
    """
    monitored_url = get_object_or_404(MonitoredURL, id=url_id)
    
    tracking_code = f'''<!-- URL Monitor Analytics -->
<script src="{request.scheme}://{request.get_host()}/tracking/{url_id}/script.js"></script>
<!-- End URL Monitor Analytics -->'''
    
    context = {
        'url': monitored_url,
        'tracking_code': tracking_code,
        'script_url': f"{request.scheme}://{request.get_host()}/tracking/{url_id}/script.js",
        'api_endpoint': f"{request.scheme}://{request.get_host()}/api/track/{url_id}/"
    }
    
    return JsonResponse(context)
