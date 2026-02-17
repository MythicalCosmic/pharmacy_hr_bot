"""
Database configuration - Works with SQLite and PostgreSQL
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
import os


# Database URL - defaults to SQLite for development
# For PostgreSQL: postgresql+asyncpg://user:pass@localhost:5432/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./hr_bot.db"
)

# Detect database type
IS_SQLITE = DATABASE_URL.startswith("sqlite")
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# Engine configuration based on database type
if IS_POSTGRES:
    # PostgreSQL with asyncpg - full optimization
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        connect_args={
            "prepared_statement_cache_size": 500,
            "statement_cache_size": 500,
        }
    )
else:
    # SQLite with aiosqlite - simpler config
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={
            "check_same_thread": False,
        }
    )

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    from database.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection"""
    await engine.dispose()


# Session manager for easy access
class SessionManager:
    """Fast session manager"""

    __slots__ = ()

    @staticmethod
    def session():
        """Get session context manager"""
        return async_session()


db = SessionManager()