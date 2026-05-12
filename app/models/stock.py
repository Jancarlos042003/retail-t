from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.product import Product


class MovementOperation(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"


class MovementType(Base):
    __tablename__ = "movement_types"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    operation: Mapped[MovementOperation] = mapped_column(Enum(MovementOperation))

    movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="movement_type"
    )


class StockLevel(Base):
    __tablename__ = "stock_levels"

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    product: Mapped["Product"] = relationship(back_populates="stock_level")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    type_id: Mapped[UUID] = mapped_column(ForeignKey("movement_types.id"))
    quantity: Mapped[int]
    reason: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    product: Mapped["Product"] = relationship(back_populates="stock_movements")
    movement_type: Mapped["MovementType"] = relationship(back_populates="movements")
