# Dockerfile
FROM python:3.11-slim

# 1) Minimal system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# 2) Python env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 3) Workdir
WORKDIR /app

# 4) Install requirements first (caches better)
COPY requirements.txt /app/
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 5) Copy the app code
COPY . /app

# 6) Non-root user
RUN useradd -ms /bin/bash appuser
USER appuser

# 7) Start the server (matches your Django project name)
CMD ["gunicorn", "readingGuide.wsgi:application", "--bind", "0.0.0.0:8000"]
