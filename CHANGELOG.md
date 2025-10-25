# Changelog

All notable changes to the URL Monitor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Changelog

All notable changes to the URL Monitor project will be documented in this file.

## [2.1.1] - 2025-10-25

### 🔥 Critical Fixes
- **Redis Session Error**: Fixed login 500 error caused by incorrect cache backend configuration
  - Changed from `django.core.cache.backends.redis.RedisCache` to `django_redis.cache.RedisCache`
  - Switched sessions to database backend (more reliable on Render free tier)
  - Fixed "AbstractConnection.__init__() got an unexpected keyword argument 'CLIENT_CLASS'" error
  - Login/register now works without Redis session dependency

### 🎨 UI Redesign - Elegant Black Theme
- **Login & Register Pages**: Reverted to elegant black/white aesthetic
  - Clean black background with white glass-morphism cards
  - Subtle backdrop blur effects
  - White gradient logo with shadow effects
  - Smooth hover animations and shine effects
  - Better contrast and readability
  - Professional minimalist design
  - Removed colorful gradients in favor of monochrome elegance

### 🛠️ Technical Improvements
- Database sessions for better reliability on free tier
- Proper django-redis backend configuration
- Removed conflicting cache options
- Better session management

## [2.1.0] - 2025-10-25

### 🎨 Major UI Redesign
- **Login & Register Pages**: Complete redesign with modern split-screen layout
  - Beautiful gradient illustration panel with floating animations
  - Clean white form panel with improved readability
  - Better mobile responsive design
  - Enhanced visual hierarchy and spacing
  - Professional iconography and branding

### ✨ New Features
- **Per-URL Analytics**: Analytics now filter by specific monitored URLs
  - Added URL selector dropdown to all analytics views
  - Analytics overview accepts `url_id` parameter
  - All analytics views (heatmap, geolocation, performance, scroll, sessions) support per-URL filtering
  - Added new URL patterns for per-URL analytics routes

### 🔧 Fixed
- **Celery URL Monitoring**: Completely redesigned task scheduling
  - Fixed `schedule_checks()` to check URLs based on their frequency setting
  - Added intelligent check scheduling (respects last check time)
  - Enhanced logging for all Celery tasks
  - Better error handling and status reporting
  - Tasks now execute immediately when scheduled (no countdown delays)

### 📊 Analytics Improvements
- **Analytics Views**: Added URL filtering to all analytics views
  - `analytics_overview(url_id=None)` - Filter by specific URL
  - `heatmap_view(url_id=None)` - Per-URL click heatmaps
  - `geolocation_view(url_id=None)` - Geographic data by URL
  - `performance_view(url_id=None)` - Web Vitals per URL
  - All views include URL dropdown selector
  - Proper user permission checks (only show user's URLs)

### 🛠️ Technical Improvements
- Enhanced Celery task logging with structured output
- Better error messages in analytics views
- Improved URL routing for analytics endpoints
- Added URL context to all analytics templates

## [2.0.10] - 2025-10-25

### Fixed
- **Analytics Error Handling**: Added comprehensive error handling to all analytics views
  - Wrapped all analytics views with `@handle_analytics_errors` decorator
  - Graceful fallback when analytics queries fail
  - Returns empty data instead of 500 errors
  - Detailed error logging for debugging

### Added
- Error recovery decorator for analytics views
- User-friendly error messages in analytics dashboards
- Comprehensive logging for all analytics operations

### Improved
- Analytics dashboard stability
- Better error messages for debugging
- Prevents 500 errors when analytics data is missing or corrupted

## [2.0.9] - 2025-10-25

### Fixed
- **Redis Connection Stability**: Enhanced Celery and Redis connection handling
  - Added connection retry logic (max 10 retries)
  - Configured connection pooling (50 max connections)
  - Added `CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP`
  - Enabled `CELERY_TASK_ACKS_LATE` for better reliability
  - Fixed "Connection to Redis lost: Retry" errors on Render free tier

### Added
- **Redis Caching**: Configured Django to use Redis for caching
  - Added `django-redis==5.4.0` to requirements
  - Configured connection pooling for cache backend
  - Set 5-second socket timeout with retry logic
  - Production sessions now use Redis for better performance

### Improved
- Better handling of Redis service restarts on free tier
- Reduced connection errors during cold starts
- More resilient task queue processing

## [2.0.8] - 2025-10-25

### Fixed
- **Analytics Foreign Key Fix**: Made `url_id` nullable in all analytics models
  - PageView, ClickHeatmap, ScrollHeatmap, MouseMovement models now allow NULL url_id
  - PerformanceMetric, SessionRecording, ConversionFunnel models now allow NULL url_id
  - Fixes "null value in column 'url_id' violates not-null constraint" errors
  - Allows tracking analytics for URL Monitor application pages (not just monitored URLs)

### Why This Was Needed
- Analytics system tracks two types of pages:
  1. **Monitored external websites** (have url_id reference)
  2. **URL Monitor app pages** (/urls/, /register/, etc. - no url_id reference)
- Previous schema required url_id, causing all app page tracking to fail
- Now analytics works for both monitored URLs and internal app pages

### Migration
- Created migration 0006: Make url field nullable with `null=True, blank=True`
- Existing data preserved, new entries can have NULL url_id

## [2.0.7] - 2025-10-25

### Fixed
- **Ultimate Migration Fix**: Moved migrations to container startup (Dockerfile CMD)
  - Created `start.sh` startup script that runs BEFORE Gunicorn starts
  - Migrations now run every time the container starts (not just during build)
  - Added database connection retry logic (30 attempts, 2-second intervals)
  - Shows detailed migration progress in container logs
  - Gunicorn only starts AFTER migrations complete successfully

### Why This Works Better
- **Build-time migrations** run during image build (before DATABASE_URL might be available)
- **Runtime migrations** run when container starts (DATABASE_URL is definitely available)
- Container won't accept traffic until migrations are done
- Every redeploy ensures database is up-to-date

### Technical Details
- `start.sh`: New startup script with migration logic
- Dockerfile: Changed CMD to run `./start.sh` instead of direct Gunicorn
- Startup sequence: Wait for DB → Run migrations → Show applied migrations → Start Gunicorn
- Gunicorn logs to stdout/stderr for Render visibility

## [2.0.6] - 2025-10-25

### Fixed
- **Critical Build Script Fix**: Simplified migration retry logic in build.sh
  - Changed from `migrate --check` (which was failing silently) to direct `migrate --noinput` with retries
  - Migrations now retry up to 30 times with 3-second intervals
  - Shows clear progress: "Migration attempt X/30..."
  - Better error messages showing actual migration output
  - Prevents build from completing without running migrations

### Technical Details
- Previous version used `migrate --check` which would fail if tables don't exist
- New version runs `migrate --noinput` directly and retries on failure
- Each retry waits 3 seconds for database to become ready
- Build fails explicitly if all 30 attempts fail
- Output is no longer suppressed (2>&1 instead of 2>/dev/null)

## [2.0.5] - 2025-10-25

### Fixed
- **Critical Database Initialization Fix**: Enhanced build.sh to properly wait for database and ensure migrations complete
  - Added database connection retry logic (30 attempts, 2-second intervals)
  - Build now fails explicitly if database isn't ready (prevents deploying without tables)
  - Added migration verification step with `showmigrations`
  - Prevents "no such table: auth_user" error on first deployment

### Technical Details
- Build script now waits up to 60 seconds for PostgreSQL to be ready
- Exits with error code 1 if database connection fails (triggers proper error in Render)
- Added verbose logging for each retry attempt
- Shows all applied migrations after successful migrate

## [2.0.3] - 2025-10-25

### Fixed
- **Critical: 500 Error After Registration** - Added error handling to dashboard view
  - Wrapped dashboard queries in try-except blocks to handle database initialization gracefully
  - Changed registration redirect from dashboard to url_list to avoid complex queries on first load
  - Added helpful error messages when database tables are still initializing
  - Prevents 500 errors when accessing dashboard before migrations complete

### Changed
- **Registration Flow** - Now redirects to URL list instead of dashboard after registration
  - Simpler page load, faster response
  - Better user experience for new accounts
  - Avoids heavy dashboard queries on fresh accounts

### Added
- **Enhanced Build Logging** - build.sh now shows detailed migration status
  - Migration check before running
  - Clear success/failure messages
  - Helps debug deployment issues on Render free tier
- **Render Free Tier Documentation** - Created comprehensive guides
  - `docs/RENDER_FREE_TIER_500_FIX.md` - Quick fix for 500 errors
  - `docs/FIX_500_ERROR.md` - Detailed troubleshooting
  - `docs/RENDER_ENVIRONMENT_SETUP.md` - Step-by-step environment setup

## [2.0.1] - 2025-10-25

### Fixed
- **Critical: Render Deployment Port Binding** - Fixed Dockerfile to use dynamic `$PORT` environment variable instead of hardcoded port 8000
  - Updated CMD to use `${PORT:-8000}` syntax (binds to $PORT if available, defaults to 8000 locally)
  - Prevents repeated service restarts on Render free tier
  - Ensures stable deployment without port conflicts

### Added
- **RENDER_TROUBLESHOOTING.md** - Comprehensive guide for debugging Render deployments
  - Port binding issues and solutions
  - Deployment checklist
  - Common issues and fixes (static files, database, CORS, Celery)
  - Performance optimization tips for free tier
  - Manual deployment steps (Blueprint vs Manual)
  - Health monitoring and uptime strategies
  - Rollback procedures

## [2.0.0] - 2025-10-25

### Added
- **External URL Tracking System**: Complete analytics tracking for monitored websites
  - Embeddable JavaScript tracking script (similar to Google Analytics)
  - CORS-enabled external tracking API endpoint
  - Visitor and session tracking with localStorage/sessionStorage
  - Event batching for performance optimization
  - No CSRF requirement for external sites
  
- **Advanced Analytics Features**:
  - Page view tracking with detailed metrics
  - Click heatmaps with element identification
  - Rage click detection (5+ clicks in 2 seconds)
  - Scroll depth tracking (25%, 50%, 75%, 100%)
  - Performance metrics (FCP, LCP, FID, CLS)
  - Session recording capabilities
  - Geographic distribution tracking
  - Device and browser analytics

- **Analytics Dashboard Views**:
  - Overview dashboard with key metrics
  - Heatmap visualization
  - Geolocation analytics
  - Performance metrics dashboard
  - Scroll depth analysis
  - Session recordings viewer

- **Template Tag System**:
  - Custom `widget_type` filter for form rendering
  - Proper form widget handling across all templates

- **Production Deployment Support**:
  - Render.com blueprint configuration (`render.yaml`)
  - Comprehensive build script (`build.sh`)
  - Docker configuration with multi-stage builds
  - Heroku Procfile support
  - WhiteNoise for static file serving
  - PostgreSQL database support via `dj-database-url`
  - Environment-based configuration

- **Documentation**:
  - Comprehensive deployment guide (`docs/RENDER_DEPLOYMENT.md`)
  - External tracking setup guide (`docs/EXTERNAL_TRACKING_GUIDE.md`)
  - Testing guide for deployed sites (`docs/TESTING_WITH_DEPLOYED_SITES.md`)
  - Analytics data flow documentation (`docs/ANALYTICS_DATA_FLOW.md`)
  - Updated README with badges and detailed sections

### Changed
- **URL Detail Page**: Added Analytics Tracking section with:
  - Feature showcase cards
  - Embeddable tracking code with copy button
  - Installation instructions
  - Example HTML implementation
  - Link to analytics dashboard

- **Settings Configuration**:
  - Added WhiteNoise middleware for static files
  - Database auto-switching between SQLite and PostgreSQL
  - Added `STATIC_ROOT` for production
  - Configured compressed static file storage
  - Updated CORS settings for external tracking

- **Requirements**: Cleaned up dependencies
  - Removed 200+ unnecessary packages
  - Added production essentials: `gunicorn`, `whitenoise`, `dj-database-url`
  - Added user-agent parsing libraries
  - Pinned stable versions
  - **Total: 16 essential packages** (from 200+)

- **Project Structure**:
  - Organized documentation in `docs/` folder
  - Removed obsolete markdown files
  - Cleaned up temporary test files
  - Updated .gitignore with comprehensive exclusions

### Fixed
- **Template Errors**: Fixed `'widget_type'` is not a registered filter error
  - Created custom template tag in `monitor/templatetags/form_filters.py`
  - Applied to all form templates requiring the filter

- **URL Routing**: Fixed namespace issues
  - Updated template URLs to use `monitor:` namespace prefix
  - Fixed reverse match errors for tracking script URLs

- **CORS Issues**: Added proper CORS headers
  - Created `add_cors_headers()` helper function
  - Handles OPTIONS preflight requests
  - Allows cross-origin external tracking

- **Static Files**: Configured for production
  - Added WhiteNoise middleware
  - Set up STATIC_ROOT and STORAGES
  - Configured compressed manifest storage

- **Database Configuration**: Production-ready setup
  - Auto-detects DATABASE_URL environment variable
  - Gracefully falls back to SQLite for development
  - Connection health checks enabled

### Removed
- Redundant `requirements_full.txt` (200+ packages)
- Temporary test files (`test_external_tracking.html`, `check_db.py`)
- Obsolete documentation (`IMPROVEMENTS.md`, `PHASE2_FEATURES.md`, `FRONTEND_REDESIGN.md`)
- Unnecessary development files

### Security
- Added comprehensive .env.example with security notes
- Configured CSRF exemption only for external tracking endpoint
- Set up proper ALLOWED_HOSTS configuration
- Added security middleware configuration notes

### Performance
- Event batching in external tracker (10 events or 5 seconds)
- Uses sendBeacon API for reliable page unload tracking
- Non-blocking asynchronous data transmission
- Redis caching for Celery tasks
- WhiteNoise for efficient static file serving

## [1.0.0] - 2025-10-24

### Added
- Initial release with core monitoring features
- URL uptime monitoring with Celery
- Email, Telegram, and Slack alerts
- Django admin interface
- Basic analytics (traffic, user flows, engagement)
- Tailwind CSS UI
- SQLite database support

---

## Version History

- **v2.0.0** (2025-10-25): External tracking system, advanced analytics, production deployment
- **v1.0.0** (2025-10-24): Initial release with core monitoring features

## Upgrade Guide

### From v1.0.0 to v2.0.0

1. **Update dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run new migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Update environment variables** (add to `.env`):
   ```bash
   DATABASE_URL=  # Optional, for PostgreSQL
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Collect static files** (for production):
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Update settings** if customized:
   - Check `url_monitor/settings.py` for new configurations
   - Ensure WhiteNoise middleware is added
   - Verify database configuration supports DATABASE_URL

6. **Test external tracking**:
   - Visit any URL detail page
   - Copy tracking code
   - Test on a local HTML file first

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Support

For issues and questions:
- GitHub Issues: https://github.com/MDhruv03/URL-Monitor/issues
- Email: dhruvmaheshwari03@gmail.com
