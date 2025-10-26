# URL Monitor Configuration

## Database Cleanup Settings

The scheduler automatically cleans up old URL status records to prevent database bloat.

### Current Configuration:

- **KEEP_RECORDS_PER_URL**: `100` records per URL
  - Keeps the 100 most recent status checks for each monitored URL
  - Older records are automatically deleted
  
- **CLEANUP_INTERVAL**: Every `5 minutes` (10 scheduler iterations × 30 seconds)
  - Cleanup runs automatically in the background
  - No manual intervention needed

- **SCHEDULER_CHECK_INTERVAL**: `30 seconds`
  - How often the scheduler checks if URLs need monitoring

### Database Space Calculations:

**Per URL with 1-minute checks:**
- 1 check/minute = 1,440 checks/day
- With 100 record limit: ~7% of daily checks stored
- Cleanup prevents unlimited growth

**Example with 10 URLs:**
- Max records: 10 URLs × 100 records = 1,000 records total
- Each record ~500 bytes = ~500 KB maximum
- Database stays small and fast!

### Adjusting Settings:

Edit `monitor/scheduler.py`:

```python
# Configuration (lines 13-16)
SCHEDULER_CHECK_INTERVAL = 30  # Seconds between checks
CLEANUP_INTERVAL = 10  # Cleanup frequency
KEEP_RECORDS_PER_URL = 100  # Records to keep per URL
```

**Recommendations:**

| Check Frequency | Recommended KEEP_RECORDS | Data Retained |
|----------------|--------------------------|---------------|
| 1 minute       | 100-200                  | ~2-3 hours    |
| 5 minutes      | 100-200                  | ~8-16 hours   |
| 10 minutes     | 100-200                  | ~16-33 hours  |
| 30 minutes     | 100-200                  | ~2-4 days     |
| 60 minutes     | 200-500                  | ~8-20 days    |

**For long-term monitoring:**
- Use higher check frequencies (30-60 min)
- Increase KEEP_RECORDS to 500-1000
- Use manual cleanup command for analytics data

### Manual Cleanup:

For analytics data (PageViews, ClickHeatmaps, etc.):

```bash
# Keep last 90 days
python manage.py cleanup_old_data --days 90

# Dry run to see what would be deleted
python manage.py cleanup_old_data --days 90 --dry-run

# Keep only 30 days
python manage.py cleanup_old_data --days 30
```

### What Gets Cleaned Automatically:

✅ **URLStatus records** - Keeps last N per URL
- Automatic cleanup every 5 minutes
- Configurable retention (default: 100 records)

### What Requires Manual Cleanup:

⚠️ **Analytics data** - Use cleanup command:
- PageViews
- ClickHeatmaps
- ScrollHeatmaps
- MouseMovements
- SessionRecordings
- PerformanceMetrics
- Notifications (read)
- TrafficMetrics
- UserFlows
- Engagement data

These require manual cleanup because you might want to keep them for longer analysis periods.

### Production Recommendations:

**Free Tier (Render/Railway):**
- KEEP_RECORDS_PER_URL: `50-100`
- Check frequency: `5-10 minutes`
- Manual cleanup: Every `30 days`

**Paid Tier (Larger DB):**
- KEEP_RECORDS_PER_URL: `200-500`
- Check frequency: `1-5 minutes`
- Manual cleanup: Every `90 days`

**High Volume Monitoring:**
- KEEP_RECORDS_PER_URL: `1000+`
- Use separate analytics database
- Consider data archival to S3/Cloud Storage

### Monitoring Database Size:

Check current database size:

```bash
# PostgreSQL
psql -d your_db -c "SELECT pg_size_pretty(pg_database_size('your_db'));"

# SQLite (local)
ls -lh db.sqlite3
```

Check URLStatus count:

```bash
python manage.py shell
>>> from monitor.models import URLStatus
>>> URLStatus.objects.count()
```

### Troubleshooting:

**Database growing too fast:**
- Reduce KEEP_RECORDS_PER_URL
- Increase check frequency (fewer checks per day)
- Run manual cleanup more often

**Need more historical data:**
- Increase KEEP_RECORDS_PER_URL
- Export data before cleanup
- Use external analytics/logging service

**Cleanup not running:**
- Check logs for scheduler errors
- Verify scheduler is running: Check `/health/` endpoint
- Should show `"scheduler": "running"`
