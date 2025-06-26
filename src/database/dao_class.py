from collections import defaultdict

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.bot.models import User

from .dao import BaseDAO
from .models import Category, OrderItems, Orders, Product


class UserDAO(BaseDAO):
    model = User


class CategoryDAO(BaseDAO):
    model = Category


class ProductDAO(BaseDAO):
    model = Product


class OrdersDAO(BaseDAO):
    model = Orders

    @classmethod
    async def find_orders_by_user(cls, session: AsyncSession, user_id: BaseModel):
        # Поиск всех заказов пользователя
        filter_dict = user_id.model_dump(exclude_unset=True)
        logger.info(f"Поиск всех заказов пользователя с ID {filter_dict}")
        try:
            query = (
                select(cls.model)
                .filter_by(**filter_dict)
                .limit(10)
                .order_by(cls.model.id.desc())
                .options(
                    joinedload(cls.model.order_items)
                    .joinedload(OrderItems.product)
                    .joinedload(Product.category)
                )
            )
            result = await session.execute(query)
            orders = result.unique().scalars().all()
            if not orders:
                return []
            all_orders = []
            for order in orders:
                # Словарь для хранения продуктов по категориям
                products_by_category = defaultdict(list)

                # Перебираем все товары в заказе
                for order_item in order.order_items:
                    product = order_item.product
                    category_name = product.category.name
                    products_by_category[category_name].append(
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "quantity": order_item.Quantity,
                        }
                    )

                # Добавляем данные заказа в итоговый список
                all_orders.append(
                    {
                        "order_id": order.id,
                        "delivery_date": order.DeliveryDate.isoformat(),
                        "products": dict(
                            products_by_category
                        ),  # Преобразуем defaultdict в обычный словарь
                    }
                )

            return all_orders
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске заказов пользователя с ID {user_id}: {e}")
            raise

    @classmethod
    async def find_orders_by_date(cls, session: AsyncSession, date: BaseModel):
        # Поиск всех заказов по дате и группировка по организациям
        filter_dict = date.model_dump(exclude_unset=True)
        logger.info(f"Поиск всех заказов по дате {filter_dict}")
        try:
            query = (
                select(cls.model)
                .filter_by(**filter_dict)
                .options(
                    joinedload(cls.model.order_items)
                    .joinedload(OrderItems.product)
                    .joinedload(Product.category)
                )
            )
            result = await session.execute(query)
            orders = result.unique().scalars().all()
            if not orders:
                return []
            all_orders = []
            for order in orders:
                # Словарь для хранения продуктов по категориям
                products_by_category = defaultdict(list)

                # Перебираем все товары в заказе
                for order_item in order.order_items:
                    product = order_item.product
                    category_name = product.category.name
                    products_by_category[category_name].append(
                        {
                            "product_id": product.id,
                            "productName": product.name,
                            "quantity": order_item.Quantity,
                        }
                    )

                # Добавляем данные заказа в итоговый список
                all_orders.append(
                    {
                        "order_id": order.id,
                        "organizationName": order.Organization,
                        "products": dict(
                            products_by_category
                        ),  # Преобразуем defaultdict в обычный словарь
                    }
                )
            logger.info(f"Найдено {len(all_orders)} заказов по дате {filter_dict}")
            return all_orders
        except Exception as e:
            logger.error(f"Ошибка при поиске заказов: {e}")
            raise


class OrderItemsDAO(BaseDAO):
    model = OrderItems
