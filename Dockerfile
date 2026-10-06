FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_phase2.txt requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_phase2.txt

# Copy application files
COPY database_persistence.py .
COPY property_analytics.py .
COPY orchestrator_v3.py .
COPY config/ ./config/
COPY scraper/ ./scraper/
COPY tests/ ./tests/

# Create logs directory
RUN mkdir -p logs

# Set environment to production
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1 || echo "SG Property Bot running"

# Run the orchestrator
CMD ["python", "-u", "orchestrator_v3.py"]

