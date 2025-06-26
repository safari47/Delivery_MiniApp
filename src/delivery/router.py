import os
from typing import Annotated, List

from aiogram.types import Update
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.bot import bot, dp
from src.bot.router import send_message_to_channel
from src.bot.utils import generate_message
from src.database.dao_class import OrderItemsDAO, OrdersDAO, ProductDAO

from .dependencies import get_redis, get_session_with_commit, get_session_without_commit
from .schemas import BaseOrder, Customer, DeliveryDate, OrderItems, OrdersIn, ProductOut

router = APIRouter()

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "../..", "templates", "page")
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    summary="Главная страница",
    description="Возвращает главную страницу приложения.",
)
async def get_main_page(request: Request) -> HTMLResponse:
    """
    Возвращает главную страницу приложения.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        TemplateResponse: HTML-шаблон главной страницы.
    """
    return templates.TemplateResponse(name="index.html", context={"request": request})


@router.get(
    "/orders",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    summary="Страница заказов",
    description="Возвращает страницу с историей заказов.",
)
async def get_orders_page(request: Request) -> HTMLResponse:
    """
    Возвращает страницу с историей заказов.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        TemplateResponse: HTML-шаблон страницы заказов.
    """
    return templates.TemplateResponse(
        name="order_history.html", context={"request": request}
    )


@router.get(
    "/products/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Получение списка продуктов",
    response_model=List[ProductOut],
    description="Возвращает список всех продуктов из базы данных.",
)
async def get_products(
    user_id: Annotated[int, Path(description="Идентификатор пользователя")],
    session: AsyncSession = Depends(get_session_without_commit),
    redis: Redis = Depends(get_redis),
) -> List[ProductOut]:
    """
    Возвращает список всех продуктов из базы данных.
    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        redis (Redis): Асинхронный клиент Redis для получения имени организации.
    Returns:
        JSONResponse: Список продуктов в формате JSON.
    """
    organization_name = await redis.get(name=user_id)
    products = await ProductDAO().find_all(session=session)
    products_list = [
        ProductOut.model_validate(product).model_dump() for product in products
    ]
    return JSONResponse(
        content={
            "products": products_list,
            "organization": (
                organization_name.decode("utf-8") if organization_name else None
            ),
        }
    )


@router.get(
    "/user_orders/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Получение заказов пользователя",
    description="Возвращает список заказов пользователя по его идентификатору.",
)
async def get_user_orders(
    user_id: Annotated[int, Path(description="Идентификатор пользователя")],
    session: AsyncSession = Depends(get_session_without_commit),
) -> JSONResponse:
    """
    Возвращает список заказов пользователя по его идентификатору.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.

    Returns:
        List[OrdersIn]: Список заказов пользователя в формате схемы OrdersIn.
    """
    orders = await OrdersDAO().find_orders_by_user(
        session=session, user_id=Customer(CustomerId=user_id)
    )
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="Заказы не найдены"
        )
    return JSONResponse(content={"orders": orders})


@router.get(
    "/orders/{date}",
    status_code=status.HTTP_200_OK,
    summary="Получение заказов по дате",
    description="Возвращает список заказов по указанной дате.",
)
async def get_orders_by_date(
    date: Annotated[str, Path(description="Дата в формате YYYY-MM-DD")],
    session: AsyncSession = Depends(get_session_without_commit),
) -> JSONResponse:
    """
    Возвращает список заказов по указанной дате.
    Args:
        date (str): Дата в формате YYYY-MM-DD.
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
    Returns:
        JSONResponse: Список заказов в формате JSON.
    """
    orders = await OrdersDAO().find_orders_by_date(
        session=session, date=DeliveryDate(DeliveryDate=date)
    )
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="Заказы не найдены"
        )
    return JSONResponse(content={"orders": orders})


@router.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    summary="Добавление заказа",
    description="Добавляет новый заказ в базу данных.",
)
async def create_order(
    orders: OrdersIn,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session_with_commit),
    redis: Redis = Depends(get_redis),
):
    """
    Добавляет новый заказ в базу данных.

    Args:
        orders (OrdersIn): Данные заказа, содержащие информацию о продуктах, дате, организации и пользователе.
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.

    Returns:
        dict: Словарь с сообщением об успешном добавлении заказа.
    """
    order = BaseOrder(**orders.model_dump())
    order_id = await OrdersDAO().add(session=session, values=(order))
    order_items = [
        OrderItems(
            OrderId=order_id.id,
            ProductId=product.id,
            Quantity=product.quantity,
        )
        for product in orders.products.values()
    ]
    await OrderItemsDAO().add_many(session=session, values=order_items)
    background_tasks.add_task(send_message_to_channel, generate_message(orders))
    await redis.set(f"{orders.CustomerId}", f"{orders.Organization}")
    return JSONResponse(
        content={"message": "Заказ успешно добавлен", "order_id": order_id.id},
    )


@router.post("/bot")
async def bot_webhook(
    request: Request, session: AsyncSession = Depends(get_session_with_commit)
) -> None:
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update, session=session)
    except Exception as e:
        logger.error(
            f"Ошибка при обработке обновления пользователя {update.message.from_user.username} с вебхука: {e}"
        )
