from datetime import date
from typing import Annotated, Dict, Union

from pydantic import BaseModel, ConfigDict, Field


class BaseProduct(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор", example=1)
    name: str = Field(..., description="Название товара", example="Морковь")
    category_id: int = Field(..., description="Идентификатор категории", example=1)
    description: str = Field(..., description="Фасовка товара", example=5)
    image: str = Field(..., description="URL изображения", example="https://example.com/carrot.jpg")
    model_config = ConfigDict(from_attributes=True)

class ProductOut(BaseProduct):
    """Модель для вывода информации о товаре"""
    pass

class ProductInOrder(BaseProduct):
    """Модель для товара в заказе"""
    quantity: Union[int, float] = Field(..., description="Количество товара в заказе", example=5)

class Customer(BaseModel):
    """Базовая модель для пользователя"""
    CustomerId: int = Field(..., description="Идентификатор пользователя, сделавшего заказ", example=12345)

class BaseOrder(Customer):
    """Базовая модель для заказа"""
    DeliveryDate: Annotated[date, Field(..., description="Дата заказа", example="2023-10-01")]
    Organization: str = Field(..., description="Название организации, сделавшей заказ", example="ООО Фермерские продукты")
    
    
class DeliveryDate(BaseModel):
    """Модель для даты доставки"""
    DeliveryDate: Annotated[date, Field(..., description="Дата доставки", example="2023-10-01")]
    
class OrdersIn(BaseOrder):
    """Модель для заказа с деталями о товарах"""
    products: Dict[str, ProductInOrder] = Field(...,description="Словарь овощей в заказе, где ключ — ID товара, а значение — информация о товаре с количеством",
        example={
            1: {
                "id": 1,
                "name": "Морковь",
                "category_id": 101,
                "description": "Свежая морковь, выращенная на ферме",
                "image": "https://example.com/carrot.jpg",
                "quantity": 5,
            },
            2: {
                "id": 2,
                "name": "Картофель",
                "category_id": 102,
                "description": "Молодой картофель, идеально подходит для запекания",
                "image": "https://example.com/potato.jpg",
                "quantity": 10,
            },
        },
    )

class OrderItems(BaseModel):
    """Модель для товара в заказе"""
    OrderId: int = Field(..., description="Идентификатор заказа", example=1)
    ProductId: int = Field(..., description="Идентификатор продукта", example=1)
    Quantity: float = Field(..., description="Количество продукта в заказе", example=5)