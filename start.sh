#!/bin/bash

# RightFax Testing & Monitoring Platform - Startup Script

echo "==============================================="
echo "RightFax Testing & Monitoring Platform"
echo "==============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before starting."
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p volumes/fcl
mkdir -p volumes/xml
mkdir -p logs
mkdir -p uploads
mkdir -p xml_archive

# Start services
echo ""
echo "Starting Docker services..."
docker compose up -d

echo ""
echo "Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."
docker compose ps

echo ""
echo "==============================================="
echo "Platform Started Successfully!"
echo "==============================================="
echo ""
echo "Access the application at:"
echo "  - Web Interface: http://localhost"
echo "  - Grafana: http://localhost:3000"
echo "  - API: http://localhost/api"
echo ""
echo "View logs with: docker compose logs -f"
echo "Stop with: docker compose down"
echo ""
