from loguru import logger
from pydantic import BaseModel

from database.dao_class import CategoryDAO, ProductDAO

from .database import async_session_maker


# Модели для создания категорий и продуктов
class CategoryCreate(BaseModel):
    name: str

class ProductCreate(BaseModel):
    name: str
    image: str
    description: str
    category_id: int

# Предварительные данные для категорий и продуктов
categories_data = [
                CategoryCreate(name="Чищенные"),
                CategoryCreate(name="Нечищенные")]

products_data = [ProductCreate(name="Картофель", image="/static/Image/Картофель_чищ.png", description="5", category_id=1),
                 ProductCreate(name="Черри", image="/static/Image/Черри_чищ.png", description="5", category_id=1),
                 ProductCreate(name="Дольки", image="/static/Image/Дольки_чищ.png", description="5", category_id=1),
                 ProductCreate(name="Лук красный", image="/static/Image/Лук_Красный_чищ.png", description="5", category_id=1),
                 ProductCreate(name="Свекла", image="/static/Image/Свекла_чищ.png", description="5", category_id=1),
                 ProductCreate(name="Морковь", image="/static/Image/Морковь_чищ.png", description="5", category_id=1),
                 ProductCreate(name="Чеснок", image="/static/Image/Чеснок_чищ.png", description="0,5", category_id=1),
                 ProductCreate(name="Лук репчатый", image="/static/Image/Лук_Репчатый_чищ.png", description="5", category_id=1),
                 ProductCreate(name="Чеснок", image="/static/Image/Чеснок_нечищ.png", description="0,5", category_id=2),
                 ProductCreate(name="Картофель", image="/static/Image/Картофель_нечищ.png", description="1", category_id=2),
                 ProductCreate(name="Морковь", image="/static/Image/Морковь_нечищ.png", description="1", category_id=2),
                 ProductCreate(name="Свекла", image="/static/Image/Свекла_нечищ.png", description="1", category_id=2),
                 ProductCreate(name="Лук репчатый", image="/static/Image/Лук_Репчатый_нечищ.png", description="1", category_id=2),
                 ProductCreate(name="Лук красный", image="/static/Image/Лук_красный_нечищ.png", description="1", category_id=2),
                 ProductCreate(name="Капуста", image="/static/Image/Капуста_нечищ.png", description="1", category_id=2)]


async def initialize_category(category=categories_data)-> None:
    async with async_session_maker() as session:
        #Проверяем, существуют ли категории
        find_category= await CategoryDAO().find_all(session=session)
        if len(find_category) > 0:
            logger.info("Категории уже существуют!")
        else:
            await CategoryDAO().add_many(session=session, values=category)
            await session.commit()
        
async def initialize_product(product=products_data)-> None:
    async with async_session_maker() as session:
        #Проверяем, существуют ли продукты
        find_product= await ProductDAO().find_all(session=session)
        if len(find_product) > 0:
            logger.info("Продукты уже существуют!")
        else:
            await ProductDAO().add_many(session=session, values=product)
            await session.commit()
