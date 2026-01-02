FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create data directory
RUN mkdir -p /app/data/chromadb

# Render uses PORT environment variable (defaults to 10000)
# The application will read PORT from environment
EXPOSE 10000

# Run the application - Render sets PORT automatically
CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
