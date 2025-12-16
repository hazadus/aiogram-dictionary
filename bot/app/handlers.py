from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from loguru import logger

from app.config import settings
from app.db import SessionLocal
from app.integrations.chatgpt import get_chatgpt_client
from app.services.translation import get_stats_text, get_translation

router = Router()
chatgpt_client = get_chatgpt_client()


# MARK: Start
@router.message(CommandStart())
async def start_command_handler(message: Message) -> None:
    """
    Обработчик команды /start.

    Отправляет приветственное сообщение пользователю с информацией о доступных командах.
    """
    if message.from_user is None:
        logger.error("Получено сообщение без данных пользователя")
        return

    user_id = message.from_user.id
    username = (
        message.from_user.username or message.from_user.first_name or "Пользователь"
    )

    logger.debug(f"Получена команда /start от пользователя {user_id} (@{username})")

    welcome_text = (
        f"👋 Привет, {username}!\n\n"
        "Этот бот умеет следующее:\n"
        "• Переводить слова и фразы на русский язык\n"
        "Используйте /help для получения списка всех команд."
    )

    await message.answer(welcome_text)


# MARK: Help
@router.message(Command("help"))
async def help_command_handler(message: Message) -> None:
    """
    Обработчик команды /help.

    Отправляет пользователю список доступных команд с их описанием.
    """
    if message.from_user is None:
        logger.error("Получено сообщение без данных пользователя")
        return

    user_id = message.from_user.id
    username = (
        message.from_user.username or message.from_user.first_name or "Пользователь"
    )

    logger.debug(f"Получена команда /help от пользователя {user_id} (@{username})")

    help_text = (
        "📋 **Доступные команды:**\n\n"
        "/start - Запустить бота и получить приветствие\n"
        "/help - Показать список доступных команд\n"
        "/stats - Показать статистику слов в базе\n"
    )

    await message.answer(help_text, parse_mode="Markdown")


# MARK: Stats
@router.message(Command("stats"))
async def stats_command_handler(message: Message) -> None:
    """
    Обработчик команды /stats.

    Отправляет пользователю подробную статистику по словам/фразам в базе данных.
    """
    if message.from_user is None:
        logger.error("Получено сообщение без данных пользователя")
        return

    user_id = message.from_user.id
    username = (
        message.from_user.username or message.from_user.first_name or "Пользователь"
    )

    logger.debug(f"Получена команда /stats от пользователя {user_id} (@{username})")

    if str(user_id) not in settings.ALLOWED_USERS:
        logger.warning(f"Пользователь {user_id} не имеет доступа к боту")
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    try:
        async with SessionLocal() as session:
            stats_text = await get_stats_text(session=session)
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await message.answer(f"❌ Произошла ошибка при получении статистики: {e}")
        return

    await message.answer(stats_text)


# MARK: Any Message
# Должно быть после остальных обработчиков команд, чтобы не перехватывать команды
@router.message()
async def message_handler(message: Message) -> None:
    """
    Обработчик всех остальных сообщений.

    Перевод текста на русский язык.
    """
    if message.from_user is None:
        logger.error("Получено сообщение без данных пользователя")
        return

    user_id = message.from_user.id
    username = (
        message.from_user.username or message.from_user.first_name or "Пользователь"
    )

    logger.debug(f"Получено сообщение от пользователя {user_id} (@{username})")

    if str(user_id) not in settings.ALLOWED_USERS:
        logger.warning(f"Пользователь {user_id} не имеет доступа к боту")
        await message.answer("❌ У вас нет доступа к этому боту.")
        return

    if message.text is None:
        logger.warning("В сообщении отсутствует текст")
        await message.answer(
            "Отправьте английское слово или словосочетание для перевода."
        )
        return

    try:
        async with SessionLocal() as session:
            translation = await get_translation(
                session=session,
                chatgpt_client=chatgpt_client,
                source=message.text,
                model=settings.OPENAI_MODEL_NAME,
            )
    except Exception as e:
        logger.error(f"Ошибка при получении перевода: {e}")
        await message.answer(f"❌ Произошла ошибка при получении перевода: {e}")
        return

    if translation is not None:
        answer_text = translation.translation

        if translation.view_count > 1:
            answer_text += f"\n\n👁️ _Количество просмотров: {translation.view_count}_"
        else:
            # Название модели выводим только при первом просмотре, т.к. текст точно был
            # переведен именно текущей моделью из конфига приложения
            answer_text += f"\n\n🧠 _Модель: {settings.OPENAI_MODEL_NAME}_"

        await message.answer(answer_text, parse_mode="Markdown")
    else:
        await message.answer("❌ Не удалось получить перевод.")
