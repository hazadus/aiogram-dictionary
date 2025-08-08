"""Содержит константы, используемые во всём приложении."""

from sqlalchemy import TextClause, text

# Используем CURRENT_TIMESTAMP в таймзоне базы данных
CURRENT_TIMESTAMP: TextClause = text("CURRENT_TIMESTAMP")
