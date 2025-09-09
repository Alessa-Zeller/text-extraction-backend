#!/bin/bash

echo "Starting PDF Processing API in production mode..."

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import asyncio
import asyncpg
import sys
import time
from app.core.config import settings

async def wait_for_db():
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = await asyncpg.connect(settings.DATABASE_URL)
            await conn.close()
            print('Database is ready!')
            return
        except Exception as e:
            print(f'Attempt {i+1}/{max_retries}: Database not ready yet... ({e})')
            await asyncio.sleep(2)
    print('Database connection failed after all retries')
    sys.exit(1)

asyncio.run(wait_for_db())
"

# Initialize database
echo "Initializing database..."
python scripts/init_db.py

# Start the application
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
