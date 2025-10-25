# URL Monitor 🚀# URL Monitor 🔍



[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)](https://www.djangoproject.com/)A comprehensive Django-based URL monitoring application that tracks website uptime, performance metrics, and sends real-time alerts when issues are detected.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)## Features ✨



A powerful Django-based application for monitoring website uptime, performance, and visitor analytics. Features real-time monitoring, advanced analytics (heatmaps, scroll tracking, performance metrics), customizable alerts, and embeddable tracking scripts for external websites.- **Real-time URL Monitoring**: Monitor multiple URLs with customizable check frequencies

- **Performance Tracking**: Track response times, status codes, and uptime percentages

## ✨ Key Features- **Smart Alerts**: Multi-channel alerting (Email, Telegram, Slack)

- **Analytics Dashboard**: Visualize uptime trends and performance metrics

### 🔍 **Website Uptime Monitoring**- **Traffic Analytics**: Monitor requests, bandwidth, and status code distribution

- Real-time uptime tracking with customizable intervals- **User Flow Tracking**: Analyze user navigation patterns

- Response time monitoring- **Engagement Metrics**: Track session duration, scroll depth, and interactions

- HTTP status code validation- **SSL Certificate Validation**: Optional SSL certificate checking

- SSL certificate checking- **Custom Thresholds**: Set custom response time and expected status code thresholds

- Historical data with charts and graphs

- Automated periodic checks via Celery## Tech Stack 🛠️



### 📊 **Advanced Analytics**- **Backend**: Django 5.2.1

- **Page View Tracking**: Monitor visitor traffic and unique visitors- **Task Queue**: Celery with Redis

- **Click Heatmaps**: Visualize where users click on your pages- **Database**: SQLite (development) / PostgreSQL (production ready)

- **Scroll Depth Analysis**: Measure how far users scroll- **Frontend**: Tailwind CSS, Django Templates

- **Performance Metrics**: Track Core Web Vitals (FCP, LCP, FID, CLS)- **Tables**: django-tables2

- **Rage Click Detection**: Identify user frustration points- **Forms**: django-crispy-forms with Tailwind styling

- **Session Recording**: Replay user interactions

- **Geographic Distribution**: See where your visitors come from## Prerequisites 📋

- **Device & Browser Analytics**: Understand your audience's technology

- Python 3.9+

### 🔔 **Smart Alerting System**- Redis Server

- Multi-channel notifications (Email, Telegram, Slack)- Node.js (for Tailwind CSS compilation)

- Configurable thresholds

- Down/Up status change alerts## Installation 🚀

- Response time breach notifications

- Real-time notification center### 1. Clone the Repository



### 🎯 **Embeddable External Tracking**```bash

- JavaScript tracking script (like Google Analytics)git clone https://github.com/MDhruv03/URL-Monitor.git

- Track visitors on your monitored websitescd URL-Monitor

- CORS-enabled for cross-origin requests```

- Privacy-focused (no personal data collection)

- Easy one-line installation### 2. Create Virtual Environment



### 🎨 **Modern User Interface**```bash

- Glass-morphism design aestheticpython -m venv venv

- Tailwind CSS responsive layoutssource venv/bin/activate  # On Windows: venv\Scripts\activate

- Real-time charts with Chart.js```

- Mobile-first responsive design

- Dark theme optimized### 3. Install Dependencies

- Intuitive navigation

```bash

## 🚀 Quick Startpip install -r requirements.txt

npm install

### Prerequisites```



- Python 3.11+### 4. Environment Configuration

- Redis Server

- Node.js & npm (for Tailwind CSS)Copy the example environment file and configure it:

- PostgreSQL (production) or SQLite (development)

```bash

### Local Development Setupcp .env.example .env

```

1. **Clone the repository**

   ```bashEdit `.env` with your configuration:

   git clone https://github.com/MDhruv03/URL-Monitor.git

   cd URL-Monitor```env

   ```SECRET_KEY=your-secret-key-here

DEBUG=True

2. **Create and activate virtual environment**ALLOWED_HOSTS=localhost,127.0.0.1

   ```bash

   python -m venv venvEMAIL_HOST=smtp.gmail.com

   EMAIL_HOST_USER=your_email@gmail.com

   # WindowsEMAIL_HOST_PASSWORD=your_app_password

   venv\Scripts\activate

   CELERY_BROKER_URL=redis://localhost:6379/0

   # Linux/Mac```

   source venv/bin/activate

   ```### 5. Database Setup



3. **Install Python dependencies**```bash

   ```bashpython manage.py migrate

   pip install -r requirements.txtpython manage.py createsuperuser

   ``````



4. **Install Node dependencies (for Tailwind)**### 6. Compile Tailwind CSS

   ```bash

   npm install```bash

   ```npm run build:css

```

5. **Set up environment variables**

   ```bash### 7. Start Redis Server

   cp .env.example .env

   # Edit .env with your configuration```bash

   ```redis-server

```

6. **Run database migrations**

   ```bash### 8. Start Celery Worker

   python manage.py migrate

   ```In a new terminal:



7. **Create a superuser account**```bash

   ```bashcelery -A url_monitor worker -l info

   python manage.py createsuperuser```

   ```

### 9. Start Celery Beat (Scheduler)

8. **Compile Tailwind CSS**

   ```bashIn another terminal:

   npm run build:css

   ``````bash

celery -A url_monitor beat -l info

9. **Start Redis** (required for Celery)```

   ```bash

   # Windows: Install from https://github.com/microsoftarchive/redis/releases### 10. Run Development Server

   redis-server

   ```bash

   # Linuxpython manage.py runserver

   sudo systemctl start redis```

   

   # MacVisit `http://localhost:8000` to access the application.

   brew services start redis

   ```## Usage 📖



10. **Start Celery Worker** (in separate terminal)### Adding a URL to Monitor

    ```bash

    celery -A url_monitor worker --loglevel=info1. Register/Login to your account

    ```2. Navigate to **URLs** → **Add URL**

3. Fill in the form:

11. **Start Celery Beat** (in another terminal)   - **Name**: Friendly name for the URL

    ```bash   - **URL**: Full URL to monitor (https://example.com)

    celery -A url_monitor beat --loglevel=info   - **Frequency**: How often to check (1, 5, 10, 30, 60 minutes)

    ```   - **Response Time Threshold**: Maximum acceptable response time (ms)

   - **Expected Status**: Expected HTTP status code (default: 200)

12. **Run development server**   - **Check SSL**: Enable SSL certificate validation

    ```bash

    python manage.py runserver### Setting Up Alerts

    ```

1. Go to **Alerts** → **Add Alert**

13. **Access the application**2. Select the URL to monitor

    - Main app: http://localhost:80003. Choose alert method:

    - Admin panel: http://localhost:8000/admin   - **Email**: Receive alerts via email

   - **Telegram**: Get notifications on Telegram

## 📦 Production Deployment   - **Slack**: Receive alerts in Slack channel

4. Enter the destination (email address, chat ID, or webhook URL)

### Quick Deploy to Render

### Dashboard Overview

1. Push code to GitHub

2. Sign up at [Render.com](https://render.com)The dashboard provides:

3. Click **New +** → **Blueprint**- Total URLs monitored

4. Connect your repository- Current up/down status

5. Click **Apply**- Average response time

- 7-day uptime trends

Render automatically sets up:- Recent notifications

- PostgreSQL database- Quick access to URL details

- Redis instance

- Web service with Gunicorn### Analytics

- SSL/HTTPS certificates

- Environment variables- **Traffic Dashboard**: View request patterns and bandwidth usage

- **User Flows**: Analyze navigation patterns with path sequences

📖 **Detailed guide**: See [`docs/RENDER_DEPLOYMENT.md`](docs/RENDER_DEPLOYMENT.md)- **Engagement Metrics**: Track session duration, scroll depth, and interactions



### Alternative Deployment Options## Project Structure 📁



- **Heroku**: Use `Procfile` and deploy with Heroku CLI```

- **Docker**: Use `docker-compose up -d`url_monitor/

- **DigitalOcean App Platform**: Deploy from GitHub├── monitor/                # Main Django app

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
