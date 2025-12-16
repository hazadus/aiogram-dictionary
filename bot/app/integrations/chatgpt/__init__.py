from app.config import settings
from app.integrations.chatgpt.client import ChatGPTClient
from app.integrations.chatgpt.exceptions import (
    ChatGPTError,
    ChatGPTHTTPError,
    ChatGPTValidationError,
)

__all__ = [
    "ChatGPTClient",
    "ChatGPTError",
    "ChatGPTHTTPError",
    "ChatGPTValidationError",
    "get_chatgpt_client",
]


def get_chatgpt_client() -> ChatGPTClient:
    """Фабрика для создания экземпляра ChatGPTClient."""
    return ChatGPTClient(
        api_key=settings.OPENAI_API_KEY,
        api_base_url=settings.OPENAI_API_BASE_URL,
    )
