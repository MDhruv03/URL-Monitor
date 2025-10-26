# Analytics Setup Guide

## Why Analytics Show "No Data"

The analytics features (Heatmaps, Geolocation, Performance, Scroll Depth) require **JavaScript tracking** to be installed on your monitored websites.

Currently, your URL Monitor only tracks:
- ✅ **Up/Down Status** - Automatic, no setup needed
- ✅ **Response Time** - Automatic, no setup needed
- ❌ **Website Analytics** - Requires tracking script installation

## How to Enable Analytics

### Step 1: Get Your Tracking Script

1. Go to your **URL list**: https://url-monitor-2xlk.onrender.com/urls/
2. Click on a URL you want to track
3. Look for the **"Tracking Instructions"** section
4. Copy the provided JavaScript code

### Step 2: Install on Your Website

Add the tracking script to your website's HTML, just before the closing `</body>` tag:

```html
<body>
    <!-- Your website content -->
    
    <!-- URL Monitor Tracking Script -->
    <script src="https://url-monitor-2xlk.onrender.com/tracking/YOUR-URL-ID/script.js"></script>
</body>
```

### Step 3: Wait for Data

Once installed:
- Analytics data starts appearing within minutes
- Heatmaps show click positions
- Geolocation shows visitor locations
- Performance tracks page load times
- Scroll depth shows how far users scroll

## What Each Analytics Section Shows

### 📊 Overview
- Total pageviews
- Unique visitors
- Average time on page
- Bounce rate
- Top pages
- Device breakdown (desktop/mobile/tablet)

### 🗺️ Heatmaps
- Click positions on your pages
- Rage clicks (frustrated users)
- Dead clicks (clicks with no response)
- Interactive heatmap visualization

### 🌍 Geolocation
- Visitor countries and cities
- Geographic distribution
- Top locations by traffic

### ⚡ Performance
- Core Web Vitals (FCP, LCP, FID, CLS)
- Page load times
- Performance scores
- Device-specific metrics

### 📏 Scroll Depth
- How far users scroll on each page
- Average scroll depth percentage
- Page-by-page breakdown

## Important Notes

1. **No tracking script = No analytics data**
   - URL monitoring (up/down) works without it
   - Analytics require the tracking script

2. **Privacy & GDPR**
   - The tracking is cookieless
   - No personal data collected
   - Only anonymous metrics (country, device, etc.)
   - Add to your privacy policy if needed

3. **Performance Impact**
   - Tracking script is lightweight (~3KB)
   - Async loading doesn't block page
   - Minimal performance impact

## Alternative: URL Monitoring Only

If you **don't need analytics**, your URL Monitor still works perfectly for:
- ✅ Uptime monitoring
- ✅ Response time tracking
- ✅ Downtime alerts
- ✅ Status history

The analytics features are **optional** - use them only if you need detailed website visitor insights!

## Testing

To verify tracking is working:
1. Install the script on your website
2. Visit your website
3. Wait 1-2 minutes
4. Check Analytics dashboard
5. Should see pageview data appearing

## Troubleshooting

**Analytics still showing "No data":**
- Verify script is in your HTML (View Page Source)
- Check browser console for errors
- Ensure your website is publicly accessible
- Try opening your website in incognito mode
- Wait a few minutes for data to appear

**Want to track multiple websites:**
- Each monitored URL has its own tracking script
- Install the correct script on each website
- Analytics will be separated per URL

## Need Help?

If analytics still don't work after installing the script:
1. Check the browser console for errors
2. Verify the tracking script URL is correct
3. Make sure your website allows external scripts
4. Check if any ad blockers are interfering
