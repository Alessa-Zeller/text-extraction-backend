#!/usr/bin/env python3
"""
Database initialization script for Railway deployment
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings


async def init_database():
    """Initialize database tables and default data"""
    try:
        # Connect to the database
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        print("Connected to database successfully")
        
        # Read and execute the init.sql file
        init_sql_path = Path(__file__).parent.parent / "init.sql"
        
        if init_sql_path.exists():
            with open(init_sql_path, 'r') as f:
                sql_content = f.read()
            
            # Split SQL content by statements and execute them
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        await conn.execute(statement)
                        print(f"✓ Executed: {statement[:50]}...")
                    except Exception as e:
                        print(f"⚠ Warning executing statement: {e}")
                        # Continue with other statements even if one fails
            
            print("✅ Database initialization completed successfully")
        else:
            print("❌ init.sql file not found")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_database())
