"""Клиент для работы с ChatGPT API."""

import httpx
from integrations.chatgpt.exceptions import (
    ChatGPTError,
    ChatGPTHTTPError,
    ChatGPTValidationError,
)
from integrations.chatgpt.schemas import ChatCompletionResponse
from loguru import logger
from pydantic import ValidationError


class ChatGPTClient:
    """Клиент для работы с ChatGPT API."""

    def __init__(
        self,
        api_key: str,
    ):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate_text(
        self,
        *,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        system_message: str,
        temperature: float = 0.5,
        max_tokens: int = 1000,
    ) -> ChatCompletionResponse:
        """
        Генерирует текст через ChatGPT API.

        Args:
            prompt: Текст запроса

        Returns:
            dict: Распарсенный JSON ответ

        Raises:
            ValueError: При ошибке парсинга JSON
            httpx.HTTPError: При ошибке HTTP запроса
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_message,
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        logger.debug(f"Отправка запроса к ChatGPT: {prompt[:100]}...")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=data)
                response.raise_for_status()

                try:
                    response_data = response.json()
                except ValueError as e:
                    logger.error(f"Ошибка парсинга JSON ответа от ChatGPT: {e}")
                    raise ChatGPTError(f"JSON parsing error: {str(e)}") from e

                try:
                    chat_response = ChatCompletionResponse(**response_data)
                except ValidationError as e:
                    logger.error(f"Ошибка валидации ответа от ChatGPT: {e}")
                    raise ChatGPTValidationError(f"Validation error: {str(e)}") from e

                generated_text = chat_response.choices[0].message.content
                logger.debug(f"Получен ответ от ChatGPT: {generated_text[:100]}...")

                return chat_response

            except httpx.HTTPError as e:
                logger.error(f"Ошибка HTTP запроса к ChatGPT: {e}")
                raise ChatGPTHTTPError(f"HTTP error: {str(e)}") from e
            except Exception as e:
                logger.error(f"Неожиданная ошибка при работе с ChatGPT: {e}")
                raise ChatGPTError(f"Unexpected error: {str(e)}") from e

    async def translate_text(
        self,
        *,
        text: str,
        target_language: str = "русский",
    ) -> str:
        """
        Переводит текст на целевой язык с помощью ChatGPT.

        Args:
            text: Текст для перевода на английском языке
            target_language: Целевой язык перевода (по умолчанию русский)
        Returns:
            str: Переведенный текст
        """
        system_message = (
            "You are a professional translator. "
            "Translate the user's text as in examples below. Include usage examples and various meanings."
            "Return the translated text with Markdown markup, without any additional comments, "
            "greetings, or explanations.\n\n"
        )
        system_message += """
Example for word:

## Deliberate – решительный

"Deliberate" на русский язык может переводиться в зависимости от контекста:

1. **Решительный** (в контексте решительного решения или действия).  
   Пример: *deliberate decision* — *решительное решение*.

2. **Усмотрительный** (в контексте тщательного рассмотрения).  
   Пример: *deliberate act* — *усмотрительное действие*.

3. **Обдуманный** (если речь идёт о тщательном планировании).  
   Пример: *deliberate plan* — *обдуманный план*.

Если контекст не указан, наиболее распространённый перевод — **"решительный"**.

----

Example for a phrase:

## Case study – тематическое исследование

"Case study" на русский язык переводится как:

1.  **Тематическое исследование** (детальный анализ конкретного примера или ситуации).
    Пример: *a case study of a successful company* — *тематическое исследование успешной компании*.

2.  **Анализ конкретного случая** (более дословный перевод).
    Пример: *The report includes a case study on the project's failure.* — *В отчет включен анализ
    конкретного случая неудачи проекта*.

Наиболее точный перевод — **"тематическое исследование"**.
"""

        prompt = (
            f"Translate the following text to {target_language}:\n\n"
            f"---\n{text}\n---"
        )

        chat_response = await self.generate_text(
            prompt=prompt,
            model="gpt-4o",
            system_message=system_message,
            temperature=0.2,  # Низкая температура для более точного перевода
        )

        translated_text = chat_response.choices[0].message.content
        return translated_text.strip()
