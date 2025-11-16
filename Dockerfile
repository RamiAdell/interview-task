FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files (if needed)
# RUN python manage.py collectstatic --noinput

# Run migrations (optional, can be done in docker-compose)
# RUN python manage.py migrate

EXPOSE 8000

# Default command: run Django development server for easier debugging in this environment
# For production use, replace with Gunicorn or your WSGI server of choice.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
