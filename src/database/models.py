from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    name = Column(String, nullable=False)
    image = Column(String, nullable=True)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItems", back_populates="product")


class Orders(Base):
    __tablename__ = "orders"

    CustomerId = Column(Integer, nullable=False)
    Organization = Column(String, nullable=False)
    DeliveryDate = Column(Date, nullable=False)

    order_items = relationship("OrderItems", back_populates="order")


class OrderItems(Base):
    __tablename__ = "order_items"

    OrderId = Column(Integer, ForeignKey("orders.id"), nullable=False)
    ProductId = Column(Integer, ForeignKey("products.id"), nullable=False)
    Quantity = Column(Float, nullable=False)

    order = relationship("Orders", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
