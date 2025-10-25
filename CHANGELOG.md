# Changelog

All notable changes to the URL Monitor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Changelog

All notable changes to the URL Monitor project will be documented in this file.

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
