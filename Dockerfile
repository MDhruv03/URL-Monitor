FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn psycopg2-binary

# Copy project
COPY . /app/

# Collect static files (will be overridden by volume in development)
RUN python manage.py collectstatic --noinput || true

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["gunicorn", "url_monitor.wsgi:application", "--bind", "0.0.0.0:8000"]
