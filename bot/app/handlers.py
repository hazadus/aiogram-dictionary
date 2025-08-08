from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from loguru import logger

from app.config import settings
from app.db import SessionLocal
from app.integrations.chatgpt import get_chatgpt_client
from app.services.translation import get_translation

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
    )

    await message.answer(help_text, parse_mode="Markdown")


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

    try:
        async with SessionLocal() as session:
            translation = await get_translation(
                session=session,
                chatgpt_client=chatgpt_client,
                source=message.text,
            )
    except Exception as e:
        logger.error(f"Ошибка при получении перевода: {e}")
        await message.answer(f"❌ Произошла ошибка при получении перевода: {e}")
        return

    if translation is not None:
        await message.answer(translation.translation, parse_mode="Markdown")
    else:
        await message.answer("❌ Не удалось получить перевод.")
