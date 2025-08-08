"""Сервис для работы с переводами."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import TranslationDAO
from app.integrations.chatgpt import ChatGPTClient
from app.models import TranslationModel
from app.schemas import TranslationCreateSchema


async def get_translation(
    *,
    session: AsyncSession,
    chatgpt_client: ChatGPTClient,
    source: str,
) -> TranslationModel | None:
    """
    Получает перевод из базы данных по исходному тексту.

    Args:
        session (AsyncSession): Объект сессии базы данных.
        source (str): Исходный текст.

    Returns:
        TranslationModel | None: Найденная модель перевода или None.
    """
    if source is None:
        return None

    if source.strip() == "":
        return None

    # Сначала пробуем найти перевод по исходному тексту в БД
    db_translation = await TranslationDAO.find_one_or_none(
        session=session,
        source=source.lower(),
    )

    if db_translation is not None:
        logger.debug(f"Найден перевод в БД для текста: {source}")
        # Увеличиваем счетчик просмотров
        db_translation.view_count += 1
        await session.commit()
        await session.refresh(db_translation)
        return db_translation

    # Если перевод не найдет, то нужно сделать перевод и сохранить его в БД
    translated_text = await chatgpt_client.translate_text(text=source)

    db_translation = await _add_translation(
        session=session,
        source=source,
        translation=translated_text,
    )
    if db_translation is not None:
        logger.debug(f"Добавлен новый перевод в БД для текста: {source}")

    return db_translation


async def _add_translation(
    *,
    session: AsyncSession,
    source: str,
    translation: str,
) -> TranslationModel | None:
    """
    Добавляет новую запись перевода в базу данных.

    Args:
        session (AsyncSession): Объект сессии базы данных.
        source (str): Исходный текст.
        translation (str): Переведенный текст.

    Returns:
        TranslationModel: Созданная модель перевода
    """
    if source is None or translation is None:
        return None

    if source.strip() == "" or translation.strip() == "":
        return None

    translation_obj = TranslationCreateSchema(
        source=source.lower(),
        translation=translation,
        view_count=1,
    )
    db_translation = await TranslationDAO.add(
        session=session,
        obj_in=translation_obj,
    )
    await session.commit()

    if db_translation:
        await session.refresh(db_translation)

    return db_translation
