from typing import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

DB_PATH = Path(__file__).parent.parent / "flashcards.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(
    DATABASE_URL, echo=False, future=True,
)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an `AsyncSession`."""
    async with AsyncSessionLocal() as session:
        yield session

#--tbdeleted--|@asynccontextmanager
#--tbdeleted--|async def get_session():
#--tbdeleted--|    """FastAPI dependency that yields an `AsyncSession`."""
#--tbdeleted--|    async with AsyncSessionLocal() as session:
#--tbdeleted--|        yield session






        
