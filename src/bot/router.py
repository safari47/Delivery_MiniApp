from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from config import bot, settings
from database.dao_class import UserDAO

from .keyboards import main_kb
from .models import TelegramIDModel, UserModel

router = Router()


@router.message(Command("start"))
async def command_start_handler(message: Message, session: AsyncSession) -> None:
    person = await UserDAO().find_one_or_none(
        session=session, filters=TelegramIDModel(telegram_id=message.from_user.id)
    )
    if not person:
        values = UserModel(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )
        await UserDAO().add(session=session, values=values)
    await message.answer_photo(
        photo=FSInputFile(path=settings.bot_photo),
        caption=(
            "👋 Добро пожаловать в наш сервис заказов овощей! "
            "Нажмите кнопку ниже, чтобы оформить заказ на очищенные овощи в вакууме "
            "или свежие овощи прямо с грядки. 🥕🍅\n\n"
            "✨ Пусть ваш день будет свежим и ярким!"
        ),
        reply_markup=main_kb(message.from_user.id),
    )


async def send_message_to_channel(message) -> None:
    try:
        await bot.send_message(settings.CHANNEL_ID, text=message)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в канал: {e}")
