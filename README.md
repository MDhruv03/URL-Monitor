# URL Monitor

Django-based URL uptime & visitor analytics (real-time checks, alerts, embeddable tracking).

## Key features
- Periodic uptime checks, response time & SSL validation  
- Multi-channel alerts (Email / Telegram / Slack)  
- Visitor analytics: pageviews, click heatmaps, scroll depth  
- Lightweight scheduler (no mandatory workers), Redis/Celery optional  
- Docker-ready, Postgres (prod) / SQLite (dev)

## Quick start
```bash
git clone https://github.com/MDhruv03/URL-Monitor.git
cd URL-Monitor
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit settings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# or: docker-compose up -d
