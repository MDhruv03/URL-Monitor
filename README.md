# URL Monitor 🔍

A comprehensive Django-based URL monitoring application that tracks website uptime, performance metrics, and sends real-time alerts when issues are detected.

## Features ✨

- **Real-time URL Monitoring**: Monitor multiple URLs with customizable check frequencies
- **Performance Tracking**: Track response times, status codes, and uptime percentages
- **Smart Alerts**: Multi-channel alerting (Email, Telegram, Slack)
- **Analytics Dashboard**: Visualize uptime trends and performance metrics
- **Traffic Analytics**: Monitor requests, bandwidth, and status code distribution
- **User Flow Tracking**: Analyze user navigation patterns
- **Engagement Metrics**: Track session duration, scroll depth, and interactions
- **SSL Certificate Validation**: Optional SSL certificate checking
- **Custom Thresholds**: Set custom response time and expected status code thresholds

## Tech Stack 🛠️

- **Backend**: Django 5.2.1
- **Task Queue**: Celery with Redis
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Tailwind CSS, Django Templates
- **Tables**: django-tables2
- **Forms**: django-crispy-forms with Tailwind styling

## Prerequisites 📋

- Python 3.9+
- Redis Server
- Node.js (for Tailwind CSS compilation)

## Installation 🚀

### 1. Clone the Repository

```bash
git clone https://github.com/MDhruv03/URL-Monitor.git
cd URL-Monitor
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
npm install
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

CELERY_BROKER_URL=redis://localhost:6379/0
```

### 5. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Compile Tailwind CSS

```bash
npm run build:css
```

### 7. Start Redis Server

```bash
redis-server
```

### 8. Start Celery Worker

In a new terminal:

```bash
celery -A url_monitor worker -l info
```

### 9. Start Celery Beat (Scheduler)

In another terminal:

```bash
celery -A url_monitor beat -l info
```

### 10. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Usage 📖

### Adding a URL to Monitor

1. Register/Login to your account
2. Navigate to **URLs** → **Add URL**
3. Fill in the form:
   - **Name**: Friendly name for the URL
   - **URL**: Full URL to monitor (https://example.com)
   - **Frequency**: How often to check (1, 5, 10, 30, 60 minutes)
   - **Response Time Threshold**: Maximum acceptable response time (ms)
   - **Expected Status**: Expected HTTP status code (default: 200)
   - **Check SSL**: Enable SSL certificate validation

### Setting Up Alerts

1. Go to **Alerts** → **Add Alert**
2. Select the URL to monitor
3. Choose alert method:
   - **Email**: Receive alerts via email
   - **Telegram**: Get notifications on Telegram
   - **Slack**: Receive alerts in Slack channel
4. Enter the destination (email address, chat ID, or webhook URL)

### Dashboard Overview

The dashboard provides:
- Total URLs monitored
- Current up/down status
- Average response time
- 7-day uptime trends
- Recent notifications
- Quick access to URL details

### Analytics

- **Traffic Dashboard**: View request patterns and bandwidth usage
- **User Flows**: Analyze navigation patterns with path sequences
- **Engagement Metrics**: Track session duration, scroll depth, and interactions

## Project Structure 📁

```
url_monitor/
├── monitor/                # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── tasks.py           # Celery tasks
│   ├── forms.py           # Django forms
│   ├── tables.py          # django-tables2 definitions
│   └── urls.py            # URL routing
├── url_monitor/           # Project configuration
│   ├── settings.py        # Django settings
│   ├── celery.py          # Celery configuration
│   └── urls.py            # Root URL configuration
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── package.json           # Node.js dependencies
```

## Configuration ⚙️

### Email Alerts (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password
3. Update `.env`:
   ```
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_16_char_app_password
   ```

### Telegram Alerts

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Update `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   ```
4. Install telegram support: `pip install python-telegram-bot`

### Slack Alerts

1. Create an Incoming Webhook in your Slack workspace
2. Update `.env`:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

## Production Deployment 🌐

### Using PostgreSQL

1. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/url_monitor
   ```

3. Update `settings.py` to use `dj-database-url`:
   ```python
   import dj_database_url
   DATABASES = {
       'default': dj_database_url.config(
           default='sqlite:///db.sqlite3',
           conn_max_age=600
       )
   }
   ```

### Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use HTTPS
- [ ] Set up proper CSRF and CORS policies
- [ ] Configure secure session cookies
- [ ] Set up rate limiting
- [ ] Use environment variables for all secrets

## API Endpoints 🔌

- `GET /api/urls/<uuid:url_id>/status/` - Get latest URL status
- `GET /api/urls/<uuid:url_id>/chart/` - Get uptime chart data
- `POST /notifications/<int:id>/read/` - Mark notification as read
- `POST /notifications/mark-all-read/` - Mark all notifications as read

## Contributing 🤝

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting 🔧

### Celery not processing tasks

- Ensure Redis is running: `redis-cli ping` (should return PONG)
- Check Celery worker logs for errors
- Verify `CELERY_BROKER_URL` in settings

### Email alerts not working

- Verify email credentials in `.env`
- Check spam folder
- For Gmail, ensure App Password is used (not regular password)

### CSS not loading

- Run `npm run build:css`
- Check `STATIC_URL` and `STATICFILES_DIRS` in settings
- Run `python manage.py collectstatic` for production

## License 📄

This project is licensed under the ISC License.

## Author ✍️

**MDhruv03**

- GitHub: [@MDhruv03](https://github.com/MDhruv03)
- Repository: [URL-Monitor](https://github.com/MDhruv03/URL-Monitor)

## Support 💬

For issues and questions:
- Open an [issue](https://github.com/MDhruv03/URL-Monitor/issues)
- Check existing documentation
- Review closed issues for solutions

---

Made with ❤️ for monitoring URLs efficiently
