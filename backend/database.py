"""
Database configuration and models
"""

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://prodentai:prodentai_password@localhost:5432/prodentai"
)

# Create async engine (using asyncpg)
engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    echo=False,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    # Import models to register them with Base
    from models import (  # noqa: F401
        BracesFAQ,
        Fact,
        NutritionLog,
        PsychologySession,
        Reminder,
        RiskAssessment,
        User,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
