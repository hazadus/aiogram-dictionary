"""Содержит базовую модель для SQLAlchemy."""

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class BaseModel(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy. Нужен для нормальной работы миграций."""

    # Определим соглашения по именованию ключей, индексов и т.д. для исключения
    # присвоения им произвольных имён базой данных:
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
