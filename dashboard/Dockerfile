# VF Live Dashboard - Production Container
FROM python:3.11-slim

LABEL maintainer="VF Development Team"
LABEL project="VisualForgeMediaV2"
LABEL component="live-dashboard"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vf-live-dashboard.py .

# Create non-root user
RUN adduser --disabled-password --gecos '' dashboard && \
    chown -R dashboard:dashboard /app
USER dashboard

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

# Run the application
CMD ["python", "vf-live-dashboard.py"]
