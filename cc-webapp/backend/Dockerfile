FROM python:3.11-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set execute permissions
RUN chmod +x db_auto_init.py

# Copy and set execute permissions for start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Start server
CMD ["/app/start.sh"]
