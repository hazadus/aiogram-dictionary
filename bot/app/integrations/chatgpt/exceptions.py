"""Исключения для работы с ChatGPT API."""


class ChatGPTError(Exception):
    """Базовое исключение для ChatGPT API."""

    pass


class ChatGPTHTTPError(ChatGPTError):
    """HTTP ошибки при работе с API."""

    pass


class ChatGPTValidationError(ChatGPTError):
    """Ошибки валидации данных."""

    pass
