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
COPY scraper/ ./scraper/

# Create required directories
RUN mkdir -p logs config tests

# Create logs directory
RUN mkdir -p logs

# Set environment to production
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Run the orchestrator
CMD ["python", "-u", "orchestrator_v3.py"]

