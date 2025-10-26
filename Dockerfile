FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Make startup script executable
RUN chmod +x start.sh

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create logs directory
RUN mkdir -p /app/logs

# Expose port (will be dynamically assigned by Render)
EXPOSE 8000

# Use startup script to run migrations and start server
CMD ["./start.sh"]