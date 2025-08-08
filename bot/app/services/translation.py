"""Сервис для работы с переводами и статистикой."""

from datetime import datetime
from typing import Sequence, Tuple

from loguru import logger
from sqlalchemy import func, select
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


# MARK: Stats
async def get_stats_text(*, session: AsyncSession) -> str:
    """Возвращает текст со статистикой по словам/фразам в БД.

    Формирует человекочитаемое сообщение со сводной информацией:
      - количество записей
      - суммарные просмотры
      - среднее число просмотров на запись
      - число записей с более чем одним просмотром
      - топ-10 записей по количеству просмотров
      - последние 5 добавленных записей
    """

    # Общие агрегаты
    total_count = (
        await session.execute(select(func.count(TranslationModel.id)))
    ).scalar_one()

    total_views = (
        await session.execute(
            select(func.coalesce(func.sum(TranslationModel.view_count), 0))
        )
    ).scalar_one()

    avg_views: float = 0.0
    if total_count and total_count > 0:
        avg_views = float(total_views) / float(total_count)

    # Дополнительные показатели
    popular_count = (
        await session.execute(
            select(func.count(TranslationModel.id)).where(
                TranslationModel.view_count > 1
            )
        )
    ).scalar_one()

    one_view_count = (
        await session.execute(
            select(func.count(TranslationModel.id)).where(
                TranslationModel.view_count == 1
            )
        )
    ).scalar_one()

    popular_pct = (popular_count / total_count * 100.0) if total_count else 0.0
    one_view_pct = (one_view_count / total_count * 100.0) if total_count else 0.0

    # Топ-10 по просмотрам
    top_rows: Sequence[Tuple[str, int]] = (
        await session.execute(
            select(TranslationModel.source, TranslationModel.view_count)
            .order_by(TranslationModel.view_count.desc(), TranslationModel.source.asc())
            .limit(10)
        )
    ).all()

    # Последние 5 добавлений
    recent_rows: Sequence[Tuple[str, datetime]] = (
        await session.execute(
            select(TranslationModel.source, TranslationModel.created_at)
            .order_by(TranslationModel.created_at.desc())
            .limit(5)
        )
    ).all()

    lines: list[str] = []
    lines.append("📊 Статистика слов")
    lines.append("")
    lines.append(f"Всего записей: {int(total_count or 0)}")
    lines.append(f"Суммарные просмотры: {int(total_views or 0)}")
    lines.append(f"Среднее просмотров на запись: {avg_views:.2f}")
    lines.append(
        f"Записей с >1 просмотром: {int(popular_count or 0)} ({popular_pct:.1f}%)"
    )
    lines.append(
        f"Записей с 1 просмотром: {int(one_view_count or 0)} ({one_view_pct:.1f}%)"
    )

    if len(top_rows) > 0:
        lines.append("")
        lines.append("Топ-10 по просмотрам:")
        for idx, (source, views) in enumerate(top_rows, start=1):
            lines.append(f"{idx}. {source} — {views}")

    if len(recent_rows) > 0:
        lines.append("")
        lines.append("Последние добавления:")
        for source, created_at in recent_rows:
            # Форматируем UTC/aware datetime человекочитаемо
            try:
                created_str = created_at.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
            except Exception:
                created_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"- {source} — {created_str}")

    return "\n".join(lines)
