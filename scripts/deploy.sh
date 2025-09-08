#!/bin/bash

# Deployment script for PDF Processing API

echo "Deploying PDF Processing API..."

# Build Docker image
echo "Building Docker image..."
docker build -t pdf-processing-api .

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo "Checking service health..."
curl -f http://localhost:8000/health || echo "API health check failed"

echo "Deployment completed!"
echo "API is available at: http://localhost:8000"
echo "Documentation is available at: http://localhost:8000/docs"
