# Use a slim Python base image
FROM python:3.12-slim

# Ensure Python output is unbuffered and pip doesn't cache packages
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies and Xvfb to allow headed Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright browsers and required OS deps for Chromium
RUN playwright install --with-deps chromium

# Copy project files
COPY . /app

# Run the scraper under Xvfb so headed Chromium can work in a container
CMD ["xvfb-run", "-a", "python", "scraper.py"]


