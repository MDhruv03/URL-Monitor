# URL Monitor 🔍# URL Monitor 🚀# URL Monitor 🔍



A powerful Django-based application for monitoring website uptime and analyzing visitor behavior with real-time tracking, advanced analytics, and customizable alerts.



[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)](https://www.djangoproject.com/)[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)](https://www.djangoproject.com/)A comprehensive Django-based URL monitoring application that tracks website uptime, performance metrics, and sends real-time alerts when issues are detected.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)



## 🚀 Features[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)## Features ✨



### **Uptime Monitoring**

- Real-time website monitoring with customizable check intervals (1-60 minutes)

- Response time tracking and uptime percentage calculationA powerful Django-based application for monitoring website uptime, performance, and visitor analytics. Features real-time monitoring, advanced analytics (heatmaps, scroll tracking, performance metrics), customizable alerts, and embeddable tracking scripts for external websites.- **Real-time URL Monitoring**: Monitor multiple URLs with customizable check frequencies

- HTTP status code validation and SSL certificate checking

- Custom thresholds for response time and expected status codes- **Performance Tracking**: Track response times, status codes, and uptime percentages

- Background scheduler (no Celery/Redis required)

- Auto-cleanup keeps database lean (100 records per URL)## ✨ Key Features- **Smart Alerts**: Multi-channel alerting (Email, Telegram, Slack)



### **Visitor Analytics**- **Analytics Dashboard**: Visualize uptime trends and performance metrics

- **Page Views**: Track unique visitors and session data

- **Click Heatmaps**: Visualize user click patterns### 🔍 **Website Uptime Monitoring**- **Traffic Analytics**: Monitor requests, bandwidth, and status code distribution

- **Scroll Depth**: Measure engagement with scroll tracking

- **Performance Metrics**: Monitor Core Web Vitals (FCP, LCP, FID, CLS)- Real-time uptime tracking with customizable intervals- **User Flow Tracking**: Analyze user navigation patterns

- **Geolocation**: Geographic distribution of visitors

- **Rage Click Detection**: Identify user frustration points- Response time monitoring- **Engagement Metrics**: Track session duration, scroll depth, and interactions



### **Alerts & Notifications**- HTTP status code validation- **SSL Certificate Validation**: Optional SSL certificate checking

- Multi-channel alerts (Email, Telegram, Slack)

- Configurable notification settings- SSL certificate checking- **Custom Thresholds**: Set custom response time and expected status code thresholds

- Real-time status change notifications

- Notification history and management- Historical data with charts and graphs



### **Analytics Dashboard**- Automated periodic checks via Celery## Tech Stack 🛠️

- Overview with key metrics and charts

- Interactive heatmaps for click visualization

- Geolocation map with country-level data

- Performance monitoring dashboard### 📊 **Advanced Analytics**- **Backend**: Django 5.2.1

- Scroll depth analysis with distribution charts

- URL-specific filtering across all views- **Page View Tracking**: Monitor visitor traffic and unique visitors- **Task Queue**: Celery with Redis



## 🛠️ Tech Stack- **Click Heatmaps**: Visualize where users click on your pages- **Database**: SQLite (development) / PostgreSQL (production ready)



- **Backend**: Django 5.2.1, Python 3.11+- **Scroll Depth Analysis**: Measure how far users scroll- **Frontend**: Tailwind CSS, Django Templates

- **Database**: SQLite (dev) / PostgreSQL (production)

- **Frontend**: Tailwind CSS, Django Templates- **Performance Metrics**: Track Core Web Vitals (FCP, LCP, FID, CLS)- **Tables**: django-tables2

- **Monitoring**: Threading-based background scheduler

- **Analytics**: JavaScript tracking script with CORS support- **Rage Click Detection**: Identify user frustration points- **Forms**: django-crispy-forms with Tailwind styling

- **Deployment**: Render (single web service, no workers needed)

- **Session Recording**: Replay user interactions

## 📋 Installation

- **Geographic Distribution**: See where your visitors come from## Prerequisites 📋

### Prerequisites

- Python 3.11+- **Device & Browser Analytics**: Understand your audience's technology

- Node.js and npm (for Tailwind CSS)

- Git- Python 3.9+



### Local Setup### 🔔 **Smart Alerting System**- Redis Server



1. **Clone the repository**- Multi-channel notifications (Email, Telegram, Slack)- Node.js (for Tailwind CSS compilation)

```bash

git clone https://github.com/MDhruv03/URL-Monitor.git- Configurable thresholds

cd URL-Monitor

```- Down/Up status change alerts## Installation 🚀



2. **Create virtual environment**- Response time breach notifications

```bash

python -m venv venv- Real-time notification center### 1. Clone the Repository

# Windows

venv\Scripts\activate

# Linux/Mac

source venv/bin/activate### 🎯 **Embeddable External Tracking**```bash

```

- JavaScript tracking script (like Google Analytics)git clone https://github.com/MDhruv03/URL-Monitor.git

3. **Install dependencies**

```bash- Track visitors on your monitored websitescd URL-Monitor

pip install -r requirements.txt

npm install- CORS-enabled for cross-origin requests```

```

- Privacy-focused (no personal data collection)

4. **Configure environment**

```bash- Easy one-line installation### 2. Create Virtual Environment

# Copy example env file

cp .env.example .env



# Edit .env with your settings:### 🎨 **Modern User Interface**```bash

# SECRET_KEY=your-secret-key

# DEBUG=True- Glass-morphism design aestheticpython -m venv venv

# ALLOWED_HOSTS=localhost,127.0.0.1

```- Tailwind CSS responsive layoutssource venv/bin/activate  # On Windows: venv\Scripts\activate



5. **Initialize database**- Real-time charts with Chart.js```

```bash

python manage.py migrate- Mobile-first responsive design

python manage.py createsuperuser

```- Dark theme optimized### 3. Install Dependencies



6. **Build Tailwind CSS**- Intuitive navigation

```bash

npm run build```bash

```

## 🚀 Quick Startpip install -r requirements.txt

7. **Run development server**

```bashnpm install

python manage.py runserver

```### Prerequisites```



Visit `http://localhost:8000` to access the application.



## 🌐 Deployment (Render)- Python 3.11+### 4. Environment Configuration



### Quick Deploy- Redis Server



1. **Push to GitHub**- Node.js & npm (for Tailwind CSS)Copy the example environment file and configure it:

```bash

git push origin main- PostgreSQL (production) or SQLite (development)

```

```bash

2. **Create Web Service on Render**

   - Connect your GitHub repository### Local Development Setupcp .env.example .env

   - Build Command: `pip install -r requirements.txt && npm install && npm run build && python manage.py migrate`

   - Start Command: `gunicorn url_monitor.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120````



3. **Configure Environment Variables**1. **Clone the repository**

```

SECRET_KEY=your-production-secret-key   ```bashEdit `.env` with your configuration:

DEBUG=False

ALLOWED_HOSTS=your-app.onrender.com   git clone https://github.com/MDhruv03/URL-Monitor.git

DATABASE_URL=your-postgres-url

```   cd URL-Monitor```env



4. **Add PostgreSQL Database**   ```SECRET_KEY=your-secret-key-here

   - Create PostgreSQL instance on Render

   - Copy `DATABASE_URL` to environment variablesDEBUG=True



The background scheduler starts automatically with the Django application - no separate worker services needed!2. **Create and activate virtual environment**ALLOWED_HOSTS=localhost,127.0.0.1



## 📊 Usage   ```bash



### Adding URLs to Monitor   python -m venv venvEMAIL_HOST=smtp.gmail.com



1. Navigate to **URLs** → **Add URL**   EMAIL_HOST_USER=your_email@gmail.com

2. Fill in:

   - **Name**: Friendly identifier   # WindowsEMAIL_HOST_PASSWORD=your_app_password

   - **URL**: Full URL to monitor (e.g., `https://example.com`)

   - **Check Frequency**: 1, 5, 10, 30, or 60 minutes   venv\Scripts\activate

   - **Expected Status**: HTTP status code (default: 200)

   - **Response Time Threshold**: Max acceptable response time in ms   CELERY_BROKER_URL=redis://localhost:6379/0

   - **SSL Check**: Enable SSL certificate validation

   # Linux/Mac```

3. Click **Save** - monitoring starts automatically!

   source venv/bin/activate

### Setting Up Visitor Analytics

   ```### 5. Database Setup

1. Navigate to your monitored URL details

2. Click **Get Tracking Script**

3. Copy the provided JavaScript snippet

4. Paste before `</body>` tag on your website:3. **Install Python dependencies**```bash



```html   ```bashpython manage.py migrate

<script src="https://your-app.onrender.com/tracking/{url-id}/script.js"></script>

```   pip install -r requirements.txtpython manage.py createsuperuser



The script automatically tracks:   ``````

- Page views with device/browser info

- Click positions for heatmaps

- Scroll depth events

- Performance metrics (Core Web Vitals)4. **Install Node dependencies (for Tailwind)**### 6. Compile Tailwind CSS

- Rage clicks and user frustration

   ```bash

### Viewing Analytics

   npm install```bash

Navigate to **Analytics** to access:

- **Overview**: Key metrics, pageviews over time, top pages   ```npm run build:css

- **Heatmaps**: Click visualization by page

- **Geolocation**: Visitor distribution map```

- **Performance**: Core Web Vitals and load times

- **Scroll Depth**: User engagement analysis5. **Set up environment variables**



Use the dropdown to filter analytics by specific URL.   ```bash### 7. Start Redis Server



### Configuring Alerts   cp .env.example .env



1. Navigate to **Alerts** → **Add Alert**   # Edit .env with your configuration```bash

2. Select URL to monitor

3. Choose notification method:   ```redis-server

   - **Email**: Receive alerts via email

   - **Telegram**: Get instant Telegram notifications```

   - **Slack**: Post alerts to Slack channel

4. Enter destination (email, bot token, webhook URL)6. **Run database migrations**

5. Click **Save**

   ```bash### 8. Start Celery Worker

Alerts trigger when:

- URL becomes unreachable (status code ≠ expected)   python manage.py migrate

- Response time exceeds threshold

- SSL certificate expires or is invalid   ```In a new terminal:



## 🏗️ Project Structure



```7. **Create a superuser account**```bash

url_monitor/

├── monitor/                    # Main Django app   ```bashcelery -A url_monitor worker -l info

│   ├── models.py              # Database models

│   ├── views.py               # Core views (monitoring, alerts)   python manage.py createsuperuser```

│   ├── analytics_views.py     # Analytics dashboard views

│   ├── external_tracking.py   # Tracking script generator   ```

│   ├── scheduler.py           # Background URL monitoring

│   ├── forms.py               # Django forms### 9. Start Celery Beat (Scheduler)

│   ├── urls.py                # URL routing

│   └── management/8. **Compile Tailwind CSS**

│       └── commands/          # Management commands

├── templates/                  # HTML templates   ```bashIn another terminal:

│   ├── base.html              # Base template

│   ├── dashboard.html         # Main dashboard   npm run build:css

│   ├── url_*.html             # URL management pages

│   ├── analytics/             # Analytics templates   ``````bash

│   └── ...

├── static/                     # Static filescelery -A url_monitor beat -l info

│   ├── css/

│   │   ├── input.css          # Tailwind input9. **Start Redis** (required for Celery)```

│   │   └── styles.css         # Compiled CSS

│   └── js/   ```bash

│       └── main.js            # Frontend JavaScript

├── url_monitor/               # Django project settings   # Windows: Install from https://github.com/microsoftarchive/redis/releases### 10. Run Development Server

│   ├── settings.py            # Main settings

│   ├── urls.py                # Project URLs   redis-server

│   └── wsgi.py                # WSGI config

├── manage.py                  # Django management   ```bash

├── requirements.txt           # Python dependencies

├── package.json               # Node dependencies   # Linuxpython manage.py runserver

├── Procfile                   # Render deployment

├── render.yaml                # Render configuration   sudo systemctl start redis```

└── README.md                  # This file

```   



## 🔧 Configuration   # MacVisit `http://localhost:8000` to access the application.



### Scheduler Settings (monitor/scheduler.py)   brew services start redis



```python   ```## Usage 📖

SCHEDULER_CHECK_INTERVAL = 30   # Check URLs every 30 seconds

CLEANUP_INTERVAL = 10           # Cleanup every 10 iterations (5 minutes)

KEEP_RECORDS_PER_URL = 100      # Keep last 100 status records per URL

```10. **Start Celery Worker** (in separate terminal)### Adding a URL to Monitor



### Environment Variables    ```bash



| Variable | Description | Default |    celery -A url_monitor worker --loglevel=info1. Register/Login to your account

|----------|-------------|---------|

| `SECRET_KEY` | Django secret key | Required |    ```2. Navigate to **URLs** → **Add URL**

| `DEBUG` | Debug mode | `True` |

| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |3. Fill in the form:

| `DATABASE_URL` | PostgreSQL URL (production) | SQLite (dev) |

11. **Start Celery Beat** (in another terminal)   - **Name**: Friendly name for the URL

## 📡 API Endpoints

    ```bash   - **URL**: Full URL to monitor (https://example.com)

### Uptime Monitoring

- `GET /health/` - Health check (scheduler status)    celery -A url_monitor beat --loglevel=info   - **Frequency**: How often to check (1, 5, 10, 30, 60 minutes)

- `GET /api/urls/{id}/status/` - Get URL status

- `GET /api/urls/{id}/chart/` - Get chart data    ```   - **Response Time Threshold**: Maximum acceptable response time (ms)

- `POST /urls/{id}/check/` - Trigger immediate check

   - **Expected Status**: Expected HTTP status code (default: 200)

### Analytics Tracking

- `GET /tracking/{id}/script.js` - Get tracking script12. **Run development server**   - **Check SSL**: Enable SSL certificate validation

- `POST /api/track/{id}/` - Receive tracking events

- `GET /tracking/{id}/instructions/` - Setup instructions    ```bash



## 🧹 Maintenance    python manage.py runserver### Setting Up Alerts



### Database Cleanup    ```



The scheduler automatically keeps the database lean by:1. Go to **Alerts** → **Add Alert**

- Maintaining only the last 100 status checks per URL

- Running cleanup every 5 minutes13. **Access the application**2. Select the URL to monitor

- No manual intervention required

    - Main app: http://localhost:80003. Choose alert method:

### Manual Cleanup (if needed)

    - Admin panel: http://localhost:8000/admin   - **Email**: Receive alerts via email

```bash

# Clean up soft-deleted URLs   - **Telegram**: Get notifications on Telegram

python manage.py cleanup_deleted_urls

## 📦 Production Deployment

# Clean old data (older than 90 days)

python manage.py cleanup_old_data --days 90> **🔧 v2.0.1 Critical Fix**: Port binding issue resolved! Dockerfile now uses dynamic `$PORT` for Render deployment. No more repeated restarts. See [`docs/RENDER_TROUBLESHOOTING.md`](docs/RENDER_TROUBLESHOOTING.md) for details.

```

### Quick Deploy to Render

## 🐛 Troubleshooting

### Dashboard Overview

### Scheduler Not Running

- Check `/health/` endpoint - should show `scheduler: "running"`1. Push code to GitHub

- Ensure application started with gunicorn or `runserver`

- Check logs for scheduler startup messages2. Sign up at [Render.com](https://render.com)The dashboard provides:



### Analytics Not Tracking3. Click **New +** → **Blueprint**- Total URLs monitored

- Verify tracking script is embedded on website

- Check CORS settings in `external_tracking.py`4. Connect your repository- Current up/down status

- Verify URL ID in tracking script matches monitored URL

- Check browser console for JavaScript errors5. Click **Apply**- Average response time



### Alerts Not Sending- 7-day uptime trends

- Verify alert configuration (method and destination)

- Check alert is active (`is_active=True`)Render automatically sets up:- Recent notifications

- Test with manual check button on URL detail page

- PostgreSQL database- Quick access to URL details

## 🤝 Contributing

- Redis instance

1. Fork the repository

2. Create feature branch (`git checkout -b feature/amazing-feature`)- Web service with Gunicorn### Analytics

3. Commit changes (`git commit -m 'Add amazing feature'`)

4. Push to branch (`git push origin feature/amazing-feature`)- SSL/HTTPS certificates

5. Open Pull Request

- Environment variables- **Traffic Dashboard**: View request patterns and bandwidth usage

## 📄 License

- **User Flows**: Analyze navigation patterns with path sequences

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

📖 **Detailed guide**: See [`docs/RENDER_DEPLOYMENT.md`](docs/RENDER_DEPLOYMENT.md)- **Engagement Metrics**: Track session duration, scroll depth, and interactions

## 🔗 Links



- **Live Demo**: [url-monitor-2xlk.onrender.com](https://url-monitor-2xlk.onrender.com)

- **Repository**: [github.com/MDhruv03/URL-Monitor](https://github.com/MDhruv03/URL-Monitor)### Alternative Deployment Options## Project Structure 📁

- **Issues**: [github.com/MDhruv03/URL-Monitor/issues](https://github.com/MDhruv03/URL-Monitor/issues)



## 📞 Support

- **Heroku**: Use `Procfile` and deploy with Heroku CLI```

For support, email your queries or open an issue on GitHub.

- **Docker**: Use `docker-compose up -d`url_monitor/

---

- **DigitalOcean App Platform**: Deploy from GitHub├── monitor/                # Main Django app

**Built with ❤️ using Django and Tailwind CSS**

- **AWS Elastic Beanstalk**: Use EB CLI│   ├── models.py          # Database models

│   ├── views.py           # View logic

## 🎯 Using External Analytics Tracking│   ├── tasks.py           # Celery tasks

│   ├── forms.py           # Django forms

### Quick Setup│   ├── tables.py          # django-tables2 definitions

│   └── urls.py            # URL routing

1. **Add URL to monitor** in your dashboard├── url_monitor/           # Project configuration

2. **Get tracking code** from URL detail page│   ├── settings.py        # Django settings

3. **Install on your website**:│   ├── celery.py          # Celery configuration

│   └── urls.py            # Root URL configuration

```html├── templates/             # HTML templates

<!DOCTYPE html>├── static/                # Static files (CSS, JS)

<html>├── manage.py              # Django management script

<head>├── requirements.txt       # Python dependencies

    <title>Your Website</title>└── package.json           # Node.js dependencies

    ```

    <!-- URL Monitor Analytics -->

    <script src="https://your-monitor.onrender.com/tracking/{url-id}/script.js"></script>## Configuration ⚙️

</head>

<body>### Email Alerts (Gmail)

    <!-- Your content -->

</body>1. Enable 2-Factor Authentication on your Gmail account

</html>2. Generate an App Password

```3. Update `.env`:

   ```

4. **View analytics** in your dashboard   EMAIL_HOST_USER=your_email@gmail.com

   EMAIL_HOST_PASSWORD=your_16_char_app_password

📖 **Detailed guide**: See [`docs/EXTERNAL_TRACKING_GUIDE.md`](docs/EXTERNAL_TRACKING_GUIDE.md)   ```



## 🛠️ Technology Stack### Telegram Alerts



**Backend**1. Create a bot via [@BotFather](https://t.me/botfather)

- Django 5.2.12. Get your chat ID from [@userinfobot](https://t.me/userinfobot)

- Celery 5.5.3 (async tasks)3. Update `.env`:

- Redis 6.2.0 (message broker)   ```

- PostgreSQL (production)   TELEGRAM_BOT_TOKEN=your_bot_token

- SQLite (development)   ```

4. Install telegram support: `pip install python-telegram-bot`

**Frontend**

- Tailwind CSS 3.x### Slack Alerts

- Chart.js (visualizations)

- Vanilla JavaScript1. Create an Incoming Webhook in your Slack workspace

- HTML5 & CSS32. Update `.env`:

   ```

**Deployment**   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

- Gunicorn (WSGI server)   ```

- WhiteNoise (static files)

- Docker support## Production Deployment 🌐

- Render/Heroku compatible

### Using PostgreSQL

**Analytics**

- Custom JavaScript tracker1. Install PostgreSQL driver:

- django-tables2   ```bash

- User agent parsing   pip install psycopg2-binary

- Geolocation lookup   ```



## 📁 Project Structure2. Update `.env`:

   ```

```   DATABASE_URL=postgresql://user:password@localhost:5432/url_monitor

url_monitor/   ```

├── monitor/                      # Main Django app

│   ├── models.py                # Database models3. Update `settings.py` to use `dj-database-url`:

│   ├── views.py                 # View controllers   ```python

│   ├── analytics_api.py         # Analytics API endpoints   import dj_database_url

│   ├── analytics_views.py       # Analytics dashboards   DATABASES = {

│   ├── external_tracking.py     # External tracking system       'default': dj_database_url.config(

│   ├── tasks.py                 # Celery background tasks           default='sqlite:///db.sqlite3',

│   ├── forms.py                 # Django forms           conn_max_age=600

│   ├── tables.py                # Table definitions       )

│   └── templatetags/            # Custom template filters   }

├── url_monitor/                 # Project configuration   ```

│   ├── settings.py              # Django settings

│   ├── urls.py                  # URL routing### Security Checklist

│   ├── celery.py                # Celery config

│   └── wsgi.py                  # WSGI application- [ ] Set `DEBUG=False` in production

├── static/                       # Static assets- [ ] Use a strong `SECRET_KEY`

│   ├── css/                     # Compiled CSS- [ ] Configure `ALLOWED_HOSTS` properly

│   │   ├── input.css            # Tailwind source- [ ] Use HTTPS

│   │   └── styles.css           # Compiled output- [ ] Set up proper CSRF and CORS policies

│   └── js/                      # JavaScript files- [ ] Configure secure session cookies

│       ├── main.js              # Main scripts- [ ] Set up rate limiting

│       └── analytics-tracker.js # Dashboard analytics- [ ] Use environment variables for all secrets

├── templates/                    # HTML templates

│   ├── base.html                # Base template## API Endpoints 🔌

│   ├── dashboard.html           # Main dashboard

│   ├── url_list.html            # URL list view- `GET /api/urls/<uuid:url_id>/status/` - Get latest URL status

│   ├── url_detail.html          # URL details & tracking- `GET /api/urls/<uuid:url_id>/chart/` - Get uptime chart data

│   └── analytics/               # Analytics templates- `POST /notifications/<int:id>/read/` - Mark notification as read

├── docs/                         # Documentation- `POST /notifications/mark-all-read/` - Mark all notifications as read

│   ├── RENDER_DEPLOYMENT.md     # Deployment guide

│   ├── EXTERNAL_TRACKING_GUIDE.md## Contributing 🤝

│   ├── TESTING_WITH_DEPLOYED_SITES.md

│   └── ANALYTICS_DATA_FLOW.mdContributions are welcome! Please follow these steps:

├── requirements.txt             # Python packages

├── package.json                 # Node packages1. Fork the repository

├── Dockerfile                   # Docker config2. Create a feature branch (`git checkout -b feature/amazing-feature`)

├── docker-compose.yml           # Docker Compose3. Commit your changes (`git commit -m 'Add amazing feature'`)

├── render.yaml                  # Render blueprint4. Push to the branch (`git push origin feature/amazing-feature`)

├── Procfile                     # Heroku config5. Open a Pull Request

├── runtime.txt                  # Python version

├── build.sh                     # Build script## Troubleshooting 🔧

└── manage.py                    # Django CLI

```### Celery not processing tasks



## ⚙️ Configuration- Ensure Redis is running: `redis-cli ping` (should return PONG)

- Check Celery worker logs for errors

### Environment Variables- Verify `CELERY_BROKER_URL` in settings



Create `.env` file in project root:### Email alerts not working



```bash- Verify email credentials in `.env`

# Django Core- Check spam folder

SECRET_KEY=your-secret-key-min-50-characters- For Gmail, ensure App Password is used (not regular password)

DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1### CSS not loading



# Database (optional - uses SQLite by default)- Run `npm run build:css`

DATABASE_URL=postgresql://user:password@localhost:5432/url_monitor- Check `STATIC_URL` and `STATICFILES_DIRS` in settings

- Run `python manage.py collectstatic` for production

# Redis & Celery

REDIS_URL=redis://localhost:6379/0## License 📄

CELERY_BROKER_URL=redis://localhost:6379/0

CELERY_RESULT_BACKEND=redis://localhost:6379/0This project is licensed under the ISC License.



# Email Notifications (optional)## Author ✍️

EMAIL_HOST=smtp.gmail.com

EMAIL_PORT=587**MDhruv03**

EMAIL_USE_TLS=True

EMAIL_HOST_USER=your-email@gmail.com- GitHub: [@MDhruv03](https://github.com/MDhruv03)

EMAIL_HOST_PASSWORD=your-app-specific-password- Repository: [URL-Monitor](https://github.com/MDhruv03/URL-Monitor)



# Telegram Notifications (optional)## Support 💬

TELEGRAM_BOT_TOKEN=your-telegram-bot-token

For issues and questions:

# Slack Notifications (optional)- Open an [issue](https://github.com/MDhruv03/URL-Monitor/issues)

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL- Check existing documentation

```- Review closed issues for solutions



## 📊 Available Analytics---



### Dashboard AnalyticsMade with ❤️ for monitoring URLs efficiently

Tracks usage of the URL Monitor application itself

### External Website Analytics
Tracks visitors to your monitored websites:
- **Traffic**: Page views, unique visitors, sessions
- **Engagement**: Time on page, scroll depth, interactions
- **Performance**: Load times, FCP, LCP, FID, CLS
- **Geography**: Country, city, region distribution
- **Technology**: Devices, browsers, operating systems
- **Behavior**: Click heatmaps, rage clicks, user flows

## 🔌 API Endpoints

```
GET  /api/urls/<uuid>/status/              # Latest URL status
GET  /api/urls/<uuid>/chart/                # Uptime chart data
POST /api/analytics/track/                  # Dashboard analytics
POST /api/track/<uuid>/                     # External tracking (CORS)
GET  /tracking/<uuid>/script.js             # Tracking script
GET  /tracking/<uuid>/instructions/         # Installation guide
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Celery not processing tasks
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Check Celery connection
celery -A url_monitor inspect active
```

### Static files not loading
```bash
# Rebuild Tailwind CSS
npm run build:css

# Collect static files (production)
python manage.py collectstatic --noinput
```

## 📖 Documentation

- [Deployment Guide](docs/RENDER_DEPLOYMENT.md) - Deploy to production
- [External Tracking Guide](docs/EXTERNAL_TRACKING_GUIDE.md) - Set up analytics
- [Testing Guide](docs/TESTING_WITH_DEPLOYED_SITES.md) - Test with deployed sites
- [Analytics Data Flow](docs/ANALYTICS_DATA_FLOW.md) - How analytics works

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Dhruv Maheshwari**
- GitHub: [@MDhruv03](https://github.com/MDhruv03)
- Email: dhruvmaheshwari03@gmail.com

## 🙏 Acknowledgments

- Django community for the excellent framework
- Tailwind CSS for the beautiful UI components
- Chart.js for data visualization
- Inspired by Microsoft Clarity and Google Analytics

---

**Made with ❤️ by Dhruv Maheshwari**

*Monitoring made simple, powerful, and beautiful.*
