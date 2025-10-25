# External URL Tracking Guide

## Overview

The URL Monitor now includes a comprehensive external tracking system that allows you to track visitors to your monitored websites (similar to Google Analytics). This is separate from the dashboard analytics that tracks users of the URL Monitor app itself.

## Two Analytics Systems

### 1. **Dashboard Analytics** (Tracks URL Monitor App Users)
- **Purpose**: Track users using the URL Monitor dashboard
- **Script**: `static/js/analytics-tracker.js`
- **API Endpoint**: `/api/analytics/track/` (requires CSRF token)
- **Integration**: Automatically loaded in `base.html`
- **Use Case**: Understand how users interact with the URL Monitor interface

### 2. **External URL Tracking** (Tracks Monitored Website Visitors)
- **Purpose**: Track visitors to your monitored external websites
- **Module**: `monitor/external_tracking.py`
- **API Endpoint**: `/api/track/{url_id}/` (CSRF-exempt for external sites)
- **Integration**: Embeddable `<script>` tag for external websites
- **Use Case**: Understand how visitors interact with your monitored websites

## How External Tracking Works

### Step 1: Get Your Tracking Code

1. Navigate to a monitored URL's detail page (e.g., `/urls/{url_id}/`)
2. Find the "Analytics Tracking" section
3. Copy the tracking code snippet:

```html
<!-- URL Monitor Analytics -->
<script src="https://your-domain.com/tracking/{url_id}/script.js"></script>
```

### Step 2: Install on Your Website

Add the tracking code to your website's `<head>` section, right before the closing `</head>` tag:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Website</title>
    
    <!-- URL Monitor Analytics -->
    <script src="https://your-domain.com/tracking/{url_id}/script.js"></script>
</head>
<body>
    <!-- Your website content -->
</body>
</html>
```

### Step 3: Data Collection Begins Automatically

Once installed, the tracking script automatically collects:

- **📄 Page Views**: Every page load is tracked
- **🖱️ Click Heatmaps**: Where users click on your pages
- **😡 Rage Clicks**: Frustrated clicking behavior (5+ clicks in 2 seconds)
- **📊 Scroll Depth**: How far users scroll (25%, 50%, 75%, 100%)
- **⚡ Performance Metrics**:
  - Page load time
  - DOM Content Loaded
  - First Contentful Paint (FCP)
  - Largest Contentful Paint (LCP)
  - First Input Delay (FID)
  - Cumulative Layout Shift (CLS)

## Technical Details

### URL-Specific Tracking

Each monitored URL gets a unique tracking script with its `url_id` baked in:
- Script URL: `/tracking/{url_id}/script.js`
- Data endpoint: `/api/track/{url_id}/`
- All analytics data is associated with the specific monitored URL

### Visitor & Session Identification

The tracking script generates unique identifiers:
- **Visitor ID**: Stored in `localStorage` (persists across sessions)
- **Session ID**: Stored in `sessionStorage` (expires when browser closes)
- Both are UUIDs (e.g., `123e4567-e89b-12d3-a456-426614174000`)

### Data Batching & Performance

To minimize network requests and improve performance:
- Events are batched in groups of **10**
- Auto-flush every **5 seconds** if batch isn't full
- Uses `sendBeacon` API for reliable page unload tracking
- Non-blocking, asynchronous data transmission

### Privacy & Security

- **No Personal Information**: Only anonymous usage data is collected
- **CSRF-Exempt Endpoint**: External sites can't have our CSRF tokens
- **No Cookies**: Uses localStorage/sessionStorage instead
- **Respect User Privacy**: Consider adding a privacy notice to your site

## Available Routes

### External Tracking Routes

| Route | Method | Purpose | Authentication |
|-------|--------|---------|----------------|
| `/tracking/{url_id}/script.js` | GET | Serves the embeddable tracking JavaScript | None |
| `/api/track/{url_id}/` | POST | Receives tracking data from external sites | CSRF-exempt |
| `/tracking/{url_id}/instructions/` | GET | Returns JSON with tracking code and instructions | Logged in |

### Analytics Dashboard Routes

| Route | Purpose |
|-------|---------|
| `/analytics/overview/` | Overview of all analytics data |
| `/analytics/heatmap/` | Click heatmap visualization |
| `/analytics/geolocation/` | Geographic distribution of visitors |
| `/analytics/performance/` | Performance metrics dashboard |
| `/analytics/scroll-depth/` | Scroll depth analysis |
| `/analytics/sessions/` | Session recordings and playback |

## Data Models

All analytics data is stored in Django models with a foreign key to `MonitoredURL`:

```python
# Each model has these core fields:
url = models.ForeignKey(MonitoredURL, ...)  # Links to monitored URL
visitor_id = models.UUIDField(...)          # Unique visitor identifier
session_id = models.UUIDField(...)          # Session identifier
timestamp = models.DateTimeField(...)       # When event occurred
```

### Models:
1. **PageView**: Page visit tracking
2. **ClickHeatmap**: Click coordinates and element info
3. **ScrollHeatmap**: Scroll depth percentages
4. **MouseMovement**: Mouse tracking (optional)
5. **SessionRecording**: Full session event streams
6. **PerformanceMetric**: Load times, FCP, LCP, FID, CLS
7. **ConversionFunnel**: Custom conversion tracking
8. **Engagement**: Time on page, interactions

## Testing Your Installation

### Quick Test

1. Open the test page: `test_external_tracking.html`
2. Open browser DevTools (F12)
3. Go to Network tab, filter for "track"
4. Interact with the page (click buttons, scroll)
5. Watch tracking requests being sent to `/api/track/{url_id}/`

### Verify Data Collection

1. Navigate to URL Monitor dashboard
2. Go to monitored URL detail page
3. Click "View Analytics Dashboard"
4. Check for collected data in various analytics views

### Check Browser Storage

In browser console:
```javascript
// Check visitor ID (persists across sessions)
localStorage.getItem('urlmonitor_visitor_id')

// Check session ID (expires with browser session)
sessionStorage.getItem('urlmonitor_session_id')
```

## Troubleshooting

### Script Not Loading

**Issue**: Tracking script returns 404
- **Solution**: Verify the `url_id` is correct and the URL exists in database
- **Check**: Visit `/tracking/{url_id}/script.js` directly to test

### CORS Errors

**Issue**: Cross-origin requests blocked
- **Solution**: Ensure `CORS_ALLOWED_ORIGINS` in `settings.py` includes your website domain
- **Alternative**: Host URL Monitor on same domain as your website

### No Data Appearing

**Issue**: Script loads but no data in dashboard
- **Check 1**: Open DevTools Network tab to see if POST requests succeed
- **Check 2**: Look for JavaScript errors in Console tab
- **Check 3**: Verify database migrations are up to date: `python manage.py migrate`
- **Check 4**: Check server logs for API endpoint errors

### Tracking Script Errors

**Issue**: JavaScript errors in browser console
- **Solution 1**: Ensure script loads before any page interactions
- **Solution 2**: Check for conflicts with other analytics scripts
- **Solution 3**: Verify browser supports required APIs (localStorage, fetch, sendBeacon)

## Performance Considerations

### Impact on Your Website

The tracking script is designed to be lightweight and non-blocking:
- **Script Size**: ~8-10 KB (minified)
- **Page Load Impact**: Negligible (async loading)
- **Network Requests**: Batched every 5 seconds or 10 events
- **CPU Usage**: Minimal (passive event listeners)

### Optimization Tips

1. **Load script in `<head>`**: Ensures early initialization
2. **Use async attribute**: Prevents blocking page render
3. **Monitor batch size**: Adjust `BATCH_SIZE` in tracking script if needed
4. **Database indexes**: Ensure indexes exist on frequently queried fields

## Advanced Usage

### Custom Event Tracking

You can extend the tracking system to track custom events:

```javascript
// Access the global tracker (if exposed)
if (window.URLMonitorTracker) {
    // Track custom events
    window.URLMonitorTracker.trackCustomEvent({
        event_type: 'custom',
        event_name: 'button_clicked',
        properties: { button_id: 'signup' }
    });
}
```

### Filtering Analytics by URL

In the analytics dashboards, add `?url={url_id}` to filter data:
```
/analytics/overview/?url=e0b90400-60f1-42fe-afef-c607cb3bc3fd
```

### Export Analytics Data

From URL detail page:
1. Click "Export CSV" or "Export JSON"
2. Data includes all analytics for that monitored URL

## Migration from Dashboard to External Tracking

If you were using the dashboard analytics thinking it tracked external visitors:

### Before (Dashboard Analytics):
```html
<!-- This tracks URL Monitor app users only -->
<script src="/static/js/analytics-tracker.js"></script>
```

### After (External Tracking):
```html
<!-- This tracks visitors to your monitored website -->
<script src="/tracking/{url_id}/script.js"></script>
```

## Next Steps

1. ✅ Install tracking code on your monitored websites
2. ✅ Test data collection with DevTools
3. ✅ View analytics in URL Monitor dashboards
4. ✅ Set up alerts based on analytics data (optional)
5. ✅ Add privacy notice to your website (recommended)

## Support & Documentation

- **API Documentation**: See `ANALYTICS_DATA_FLOW.md` for detailed API specs
- **Code Reference**: `monitor/external_tracking.py` contains full implementation
- **Database Schema**: `monitor/models.py` defines all analytics models
- **Dashboard Code**: `monitor/analytics_views.py` for visualization examples

---

**Note**: This external tracking system respects user privacy and is designed for legitimate website analytics. Always comply with privacy laws (GDPR, CCPA, etc.) and inform users about data collection on your website.
