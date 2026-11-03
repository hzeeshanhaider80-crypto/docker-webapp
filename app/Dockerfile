# Start from the official small Python 3.12 image (Debian "slim").
FROM python:3.12-slim

# Build argument: the pipeline passes the git commit ID here.
ARG APP_VERSION=local

# PYTHONDONTWRITEBYTECODE: don't create .pyc files (smaller, cleaner image).
# PYTHONUNBUFFERED: print logs immediately (so 'docker logs' shows them live).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}

# All following commands run inside /app in the image.
WORKDIR /app

# Create a normal (non-root) user to run the app — safer if the app is ever hacked.
RUN useradd --create-home appuser

# Copy ONLY requirements first: Docker caches this layer, so packages are not
# re-installed on every build unless requirements.txt changes (faster builds).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code (files in .dockerignore are skipped).
COPY . .

# From here on, run as the non-root user.
USER appuser

# Documentation: the app listens on port 5000.
EXPOSE 5000

# Docker checks every 30 s that /health answers; marks the container unhealthy otherwise.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)" || exit 1

# Run with Gunicorn (a production web server), 2 workers, on all interfaces port 5000.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
