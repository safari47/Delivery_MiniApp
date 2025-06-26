from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.config import settings


def main_kb(user_id):
    builder = InlineKeyboardBuilder()

    # Кнопка для оформления заказа
    builder.button(
        text="🛒 Оформить заказ",
        web_app=WebAppInfo(url=settings.BASE_URL),
    )

    # Кнопка для просмотра заявок (только для администраторов)
    if user_id in settings.ADMIN_IDS:
        builder.button(
            text="📋 Посмотреть заявки",
            web_app=WebAppInfo(url=f"{settings.BASE_URL}/orders"),
        )
    builder.adjust(1)  # Настройка количества кнопок в строке
    return builder.as_markup()
