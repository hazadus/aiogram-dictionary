"""Содержит модель перевода."""

from datetime import datetime

import sqlalchemy as sa
from constants import CURRENT_TIMESTAMP
from models.base_model import BaseModel
from sqlalchemy.orm import Mapped, mapped_column


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
