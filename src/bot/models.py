from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)


class TelegramIDModel(BaseModel):
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(TelegramIDModel):
    first_name: str | None
    last_name: str | None
    username: str | None
