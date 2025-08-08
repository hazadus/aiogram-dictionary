"""Содержит модель перевода."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import CURRENT_TIMESTAMP
from app.models.base_model import BaseModel


class TranslationModel(BaseModel):
    """Модель перевода."""

    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Исходный текст",
    )
    translation: Mapped[str] = mapped_column(
        sa.Text(),
        nullable=False,
        comment="Переведённый текст",
    )
    view_count: Mapped[int] = mapped_column(
        sa.Integer(),
        nullable=False,
        default=0,
        comment="Количество просмотров перевода",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        server_default=CURRENT_TIMESTAMP,
        comment="Дата и время создания записи о городе",
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        server_default=CURRENT_TIMESTAMP,
        onupdate=CURRENT_TIMESTAMP,
        comment="Дата и время изменения записи о городе",
    )
