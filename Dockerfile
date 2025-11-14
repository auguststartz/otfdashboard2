FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/xml_archive /app/uploads

# Expose port
EXPOSE 5000

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
