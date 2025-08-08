from app.db.base_dao import BaseDAO
from app.models import TranslationModel
from app.schemas import TranslationCreateSchema, TranslationUpdateSchema


class TranslationDAO(
    BaseDAO[TranslationModel, TranslationCreateSchema, TranslationUpdateSchema]
):
    """Класс для работы с переводами в базе данных."""

    model: type[TranslationModel] = TranslationModel
