"""
Database initialization script.

Creates tables and initializes the database connection.
"""

import asyncio
from src.database import get_db_manager


async def init_database():
    """Initialize the database."""
    print("🗄️  Initializing database...")
    
    db = get_db_manager()
    
    try:
        await db.create_tables()
        print("✅ Database tables created successfully!")
        
        # Health check
        if await db.health_check():
            print("✅ Database connection healthy")
        else:
            print("❌ Database health check failed")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(init_database())
