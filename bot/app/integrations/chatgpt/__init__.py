from config import settings
from integrations.chatgpt.client import ChatGPTClient
from integrations.chatgpt.exceptions import (
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
    return ChatGPTClient(api_key=settings.OPENAI_API_KEY)
