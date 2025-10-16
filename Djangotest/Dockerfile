# Stage 1: Base build stage
FROM python:3.13-slim

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Install system dependencies (gcc, mysql-client for MySQL database connection, curl for Node.js)
RUN apt update \
    && apt install -y \
    gcc \
    default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
RUN pip install --upgrade pip 

# Copy the requirements file first (better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create staticfiles folder for collectstatic
RUN mkdir -p /app/staticfiles

# Set permissions (optional, depends on container user)
RUN chown -R www-data:www-data /app/staticfiles

# Expose the debug & application port
EXPOSE 5678 
EXPOSE 8000 

# Command to wait for DB, run migrations, collect static, then start Gunicorn
CMD ["sh", "-c", "\
    python manage.py wait_for_db && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application \
    "]