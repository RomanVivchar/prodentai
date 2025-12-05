"""
Database configuration for Telegram Bot
"""

from config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Create async engine
engine = create_async_engine(
    Config.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
)

# Create session factory
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database connection"""
    try:
        async with engine.begin() as conn:
            # Test connection
            await conn.execute(text("SELECT 1"))
        print("Database connection established")
    except Exception as e:
        print(f"Database connection failed: {e}")
        # Don't raise - allow bot to start even if DB is not available
        print("Warning: Bot will continue without database connection")
