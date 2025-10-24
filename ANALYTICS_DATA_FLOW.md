# Analytics System - Data Flow Documentation

## Overview
The analytics system tracks user behavior similar to Microsoft Clarity using a client-side JavaScript tracker and Django backend.

## Data Flow

### 1. **Client-Side Tracking** (`static/js/analytics-tracker.js`)

#### Initialization
```javascript
// Auto-initializes on page load via base.html
window.analyticsTracker = new AnalyticsTracker({
    apiEndpoint: '/api/analytics/track/',
    batchSize: 10,
    flushInterval: 5000
});
```

#### Events Collected

**A. Page Views** (Sent immediately)
- URL, title, referrer
- Device type (desktop/mobile/tablet)
- Browser, OS
- Screen resolution, viewport size
- Visitor ID (persistent in localStorage)
- Session ID (per-session in sessionStorage)

**B. Clicks** (Batched)
- X/Y coordinates
- Element tag, ID, class, text
- Viewport dimensions
- Session and visitor IDs

**C. Scroll Depth** (Batched, debounced 150ms)
- Maximum scroll percentage reached
- Scroll event timeline

**D. Rage Clicks** (Sent immediately)
- 3+ clicks within 1 second in same 20px area
- Position, element info, click count

**E. Dead Clicks** (Batched)
- Clicks on non-interactive elements
- Position, element selector

**F. Performance Metrics** (Sent on page load)
- **Core Web Vitals:**
  - FCP (First Contentful Paint)
  - LCP (Largest Contentful Paint)
  - FID (First Input Delay)
  - CLS (Cumulative Layout Shift)
  - TTI (Time to Interactive)
- DOM load time
- Page load time
- Connection type

**G. Page Leave** (Sent via sendBeacon on unload)
- Total time on page
- Final scroll depth
- Scroll events history
- Total clicks

### 2. **Event Batching & Sending**

```javascript
// Events are queued
queueEvent(data) {
    this.eventQueue.push(data);
    if (this.eventQueue.length >= 10) {
        this.flush(); // Send batch
    }
}

// Auto-flush every 5 seconds
setInterval(() => this.flush(), 5000);

// Critical events sent immediately
sendImmediately(data) {
    fetch('/api/analytics/track/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ events: [data] })
    });
}
```

### 3. **Backend API** (`monitor/analytics_api.py`)

#### Endpoint: `POST /api/analytics/track/`

**Request Format:**
```json
{
    "events": [
        {
            "type": "pageview",
            "session_id": "abc123",
            "visitor_id": "xyz789",
            "page_url": "/dashboard/",
            "device_type": "desktop",
            "timestamp": "2025-10-24T12:00:00Z"
        }
    ]
}
```

#### Processing Steps:

1. **Extract Request Data**
   ```python
   ip_address = get_client_ip(request)
   user_agent = request.META.get('HTTP_USER_AGENT')
   ```

2. **Get Geolocation** (via ipapi.co)
   ```python
   geo_data = get_geolocation(ip_address)
   # Returns: country, city, latitude, longitude, timezone
   ```

3. **Parse User Agent**
   ```python
   user_agent = parse(user_agent_string)
   device_type = 'mobile' if user_agent.is_mobile else 'desktop'
   browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
   os = f"{user_agent.os.family} {user_agent.os.version_string}"
   ```

4. **Save to Database**
   - `PageView` → pageview events
   - `ClickHeatmap` → click events
   - `ScrollHeatmap` → scroll events (aggregated)
   - `MouseMovement` → rage_click, dead_click
   - `PerformanceMetric` → performance events
   - `SessionRecording` → page_leave events

**Response:**
```json
{
    "status": "success",
    "processed": 5
}
```

### 4. **Database Models**

#### PageView
```python
- session_id, visitor_id
- page_url, page_title, referrer
- time_on_page, scroll_depth
- device_type, browser, os
- ip_address, country, city, latitude, longitude
- timestamp
```

#### ClickHeatmap
```python
- page_url
- x_position, y_position
- viewport_width, viewport_height
- element_tag, element_id, element_class, element_text
- session_id, device_type
- timestamp
```

#### ScrollHeatmap (Aggregated Daily)
```python
- page_url, date
- depth_distribution (JSON: {"0-10": 50, "10-20": 30, ...})
- total_views, average_depth
```

#### MouseMovement
```python
- movement_type (rage_click, dead_click, error_click, hover)
- page_url, session_id
- x_position, y_position
- click_count, element_selector
- timestamp
```

#### PerformanceMetric
```python
- page_url, session_id
- first_contentful_paint, largest_contentful_paint
- first_input_delay, cumulative_layout_shift
- time_to_interactive
- dom_load_time, page_load_time
- connection_type, effective_bandwidth
- timestamp
```

#### SessionRecording
```python
- session_id
- start_time, end_time
- events (JSON timeline)
- pages_visited, total_clicks
- had_rage_clicks
```

### 5. **Analytics Dashboards** (`monitor/analytics_views.py`)

#### Overview Dashboard (`/analytics/`)
- Total pageviews, unique visitors
- Average time on page, bounce rate
- Pageviews by day chart
- Device/browser breakdown
- Top pages, top countries

#### Heatmap (`/analytics/heatmap/`)
- Click heatmap visualization
- Rage clicks (user frustration)
- Dead clicks (usability issues)
- Top clicked elements

#### Geolocation (`/analytics/geolocation/`)
- Visitor map (country/city)
- Geographic statistics
- Engagement by location

#### Performance (`/analytics/performance/`)
- Core Web Vitals dashboard
- Performance trends over time
- Performance by page
- Google's scoring thresholds

#### Scroll Depth (`/analytics/scroll/`)
- Scroll depth by page
- Distribution visualization
- Percentage reaching bottom

#### Sessions (`/analytics/sessions/`)
- Session recordings list
- Timeline of user actions
- Pages visited in session

### 6. **Testing**

Visit `/analytics/test/` to:
- See live tracking events in debug console
- Test click tracking
- Test rage click detection
- Test scroll tracking
- Monitor network requests

The debug console shows:
```
[12:00:00] ✅ Analytics tracker is loaded
[12:00:00] Visitor ID: abc123xyz
[12:00:00] Session ID: session789
[12:00:00] Endpoint: /api/analytics/track/
[12:00:05] 📤 Sending to: /api/analytics/track/
[12:00:05] 📦 Events: 3 events
[12:00:05]    - pageview
[12:00:05]    - click
[12:00:05]    - scroll
[12:00:05] ✅ Response: 200 OK
```

## Key Features

✅ **Automatic Tracking** - No manual instrumentation needed
✅ **Privacy-Aware** - Visitor IDs are anonymous, no PII collected
✅ **Performance** - Event batching reduces server load
✅ **Reliable** - SendBeacon API ensures data delivery on page unload
✅ **Real-time** - Critical events (pageview, rage clicks) sent immediately
✅ **Geolocation** - IP-based location tracking
✅ **Web Vitals** - Google's Core Web Vitals monitoring
✅ **Heatmaps** - Visual click and scroll patterns
✅ **Session Replay** - Timeline of user actions

## Privacy & GDPR Compliance

- No cookies used (localStorage/sessionStorage only)
- Visitor IDs are anonymous random strings
- IP addresses stored but not exposed in UI
- Can be extended with consent management
- Data retention configurable via Django admin

## Performance Impact

- JavaScript bundle: ~15KB minified
- Network: Batched requests every 5 seconds
- Database: Indexed queries for fast analytics
- Async processing: Non-blocking event storage

## Next Steps

1. **Add Geolocation Map** - Integrate Leaflet.js for world map
2. **Session Replay Player** - Video-like playback of sessions
3. **Real-time Dashboard** - WebSocket updates for live metrics
4. **Alerts** - Notify on high rage clicks or poor performance
5. **A/B Testing** - Track conversion funnels
6. **Export** - CSV/PDF reports
