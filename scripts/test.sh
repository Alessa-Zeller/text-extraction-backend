#!/bin/bash

# Test script for PDF Processing API

echo "Running tests for PDF Processing API..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with pytest
echo "Running unit tests..."
pytest tests/ -v --tb=short

# Run linting (if flake8 is installed)
if command -v flake8 &> /dev/null; then
    echo "Running linting..."
    flake8 app/ --max-line-length=88 --ignore=E203,W503
fi

# Check type hints (if mypy is installed)
if command -v mypy &> /dev/null; then
    echo "Running type checking..."
    mypy app/ --ignore-missing-imports
fi

echo "Tests completed!"
