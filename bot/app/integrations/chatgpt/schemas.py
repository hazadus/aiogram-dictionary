"""Схемы для работы с ChatGPT API."""

from typing import Any

from pydantic import BaseModel


# Схема для вложенного сообщения
class ChatMessage(BaseModel):
    role: str
    content: str
    refusal: Any  # Может быть None или другой тип
    annotations: list


# Схема для одного варианта ответа
class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    logprobs: Any  # Может быть None или другой тип
    finish_reason: str


# Детали токенов
class TokenDetails(BaseModel):
    cached_tokens: int = 0
    audio_tokens: int = 0


class CompletionTokenDetails(BaseModel):
    reasoning_tokens: int = 0
    audio_tokens: int = 0
    accepted_prediction_tokens: int = 0
    rejected_prediction_tokens: int = 0


# Схема использования токенов
class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: TokenDetails
    completion_tokens_details: CompletionTokenDetails


# Основная схема ответа API
class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatChoice]
    usage: Usage
    service_tier: str
    system_fingerprint: Any  # Может быть None или
