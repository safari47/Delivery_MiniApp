# Импортируем необходимые библиотеки
import os
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


# Класс для хранения настроек бота
class Settings(BaseSettings):
    BOT_TOKEN: str  # Токен для Telegram-бота
    ADMIN_IDS: List[int]  # ID администратора
    CHANNEL_ID: str  # ID канала для публикаций
    BASE_URL: str  # Базовый URL для бота
    DB_URL: str  # URL базы данных
    REDIS_URL: str  # URL Redis для кэширования

    FORMAT_LOG: str = (
        "{time:YYYY-MM-DD в HH:mm:ss} | {level} | {message}"  # Формат лога
    )
    LOG_ROTATION: str = "10 MB"  # Размер вращения лога

    # Загрузка переменных окружения из файла .env
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    @property
    def hook_url(self) -> str:
        """Возвращает URL вебхука"""
        return f"{self.BASE_URL}/bot"

    @property
    def bot_photo(self) -> str:
        """Возвращает URL фотографии бота"""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "templates",
            "static",
            "Image",
            "start_bot.jpg",
        )


# Получаем параметры настроек
settings = Settings()

# Инициализируем aiogram-бота и диспетчер
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher(storage=MemoryStorage())

# Настройка логирования через loguru
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(
    log_file_path,
    format=settings.FORMAT_LOG,
    level="INFO",
    rotation=settings.LOG_ROTATION,
)
