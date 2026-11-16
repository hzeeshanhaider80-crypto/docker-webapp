
# Official lightweight Python image
FROM python:3.12-slim

# Application version
ARG APP_VERSION=local

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}

# Application directory
WORKDIR /app

# Create non-root user
RUN useradd --create-home appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files explicitly
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Set permissions for application user
RUN chown -R appuser:appuser /app

# Run as non-root user
USER appuser

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)" || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]

 
