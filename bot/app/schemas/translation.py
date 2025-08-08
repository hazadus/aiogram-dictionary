"""Схемы для работы с переводами."""

from pydantic import BaseModel, Field


class TranslationBaseSchema(BaseModel):
    """Базовая схема для перевода."""

    source: str = Field(..., title="Исходный текст")
    translation: str = Field(..., title="Переведённый текст")
    view_count: int = Field(
        default=1,
        title="Количество просмотров перевода",
    )


class TranslationCreateSchema(TranslationBaseSchema):
    """Схема для создания перевода."""


class TranslationUpdateSchema(TranslationBaseSchema):
    """Схема для обновления перевода."""
