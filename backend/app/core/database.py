import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from backend.app.core.config import get_settings

settings = get_settings()

os.makedirs(os.path.dirname(settings.SQLITE_DB) or ".", exist_ok=True)

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    future=True,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with async_engine.begin() as conn:
        from backend.app.models.models import (
            User, Document, ChatHistory, Machine, MaintenanceLog
        )
        await conn.run_sync(Base.metadata.create_all)


def init_db_sync():
    from backend.app.models.models import (
        User, Document, ChatHistory, Machine, MaintenanceLog
    )
    Base.metadata.create_all(bind=sync_engine)
