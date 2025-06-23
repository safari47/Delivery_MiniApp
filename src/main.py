import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from bot.bot import start_bot
from config import bot, dp, settings
from database.database import create_tables
from database.utils import initialize_category, initialize_product
from delivery.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")
    logger.info("Создание таблиц в базе данных...")
    await create_tables()
    logger.info("Инициализация категорий...")
    await initialize_category()
    logger.info("Инициализация продуктов...")
    await initialize_product()
    logger.info("Запуск бота...")
    await start_bot()
    webhook_url = settings.hook_url
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    yield
    logger.info("Завершение работы приложения...")


app = FastAPI(title="Оптовая продажа овощей", lifespan=lifespan)
# Отключаем логирование для статических файлов
logging.getLogger("uvicorn.access").disabled = True
# Инициализация статики
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
# Регистрация маршрутов
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
