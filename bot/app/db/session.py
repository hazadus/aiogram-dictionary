"""Модуль для управления асинхронными сессиями базы данных с использованием SQLAlchemy."""

from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    url=str(settings.ASYNC_POSTGRES_URI),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Проверяет соединения перед использованием
    pool_recycle=3600,  # Переиспользует соединения каждый час
)


SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
