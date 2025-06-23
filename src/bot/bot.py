from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger

from config import bot, dp

from .router import router as user_router


# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command="start", description="Запуск бота")]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def start_bot():
    # Установка команд бота
    await set_commands()
    # Регистрация роутера
    dp.include_router(user_router)
    # Запуск бота
    logger.success("Бот запущен")
