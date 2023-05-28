from typing import Optional

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserFlightDirection(Base):
    __tablename__ = "flight_direction"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    start_code: Mapped[str]
    start_name: Mapped[str]
    end_code: Mapped[str]
    end_name: Mapped[str]
    price: Mapped[Optional[int]]
    with_transfer: Mapped[bool]
    departure_at: Mapped[str]
    return_at: Mapped[Optional[str]]
