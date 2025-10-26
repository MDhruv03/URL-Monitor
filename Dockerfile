FROM python:3.11-slimFROM python:3.11-slim



# Set environment variables# Set environment variables

ENV PYTHONDONTWRITEBYTECODE=1ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1ENV PYTHONUNBUFFERED=1

ENV DEBIAN_FRONTEND=noninteractiveENV DEBIAN_FRONTEND=noninteractive



# Set work directory# Set work directory

WORKDIR /appWORKDIR /app



# Install system dependencies# Install system dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \RUN apt-get update && apt-get install -y --no-install-recommends \

    postgresql-client \    postgresql-client \

    gcc \    gcc \

    python3-dev \    python3-dev \

    libpq-dev \    libpq-dev \

    build-essential \    build-essential \

    && rm -rf /var/lib/apt/lists/*    && rm -rf /var/lib/apt/lists/*



# Upgrade pip# Upgrade pip

RUN pip install --no-cache-dir --upgrade pipRUN pip install --no-cache-dir --upgrade pip



# Install Python dependencies# Install Python dependencies

COPY requirements.txt /app/COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txtRUN pip install --no-cache-dir -r requirements.txt



# Copy project# Copy project

COPY . /app/COPY . /app/



# Make startup script executable# Make startup script executable

RUN chmod +x start.shRUN chmod +x start.sh



# Collect static files# Collect static files

RUN python manage.py collectstatic --noinput || trueRUN python manage.py collectstatic --noinput || true



# Create logs directory# Create logs directory

RUN mkdir -p /app/logsRUN mkdir -p /app/logs



# Expose port (will be dynamically assigned by Render)# Expose port (will be dynamically assigned by Render)

EXPOSE 8000EXPOSE 8000



# Use startup script to run migrations and start server# Use startup script to run migrations and start server

CMD ["./start.sh"]CMD ["./start.sh"]

