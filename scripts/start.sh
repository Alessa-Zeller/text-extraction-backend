#!/bin/bash

# Start script for PDF Processing API

echo "Starting PDF Processing API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads

# Run database migrations (if using Alembic in the future)
# alembic upgrade head

# Start the application
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
