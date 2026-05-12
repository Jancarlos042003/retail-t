from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.product_price import ProductPrice
    from app.models.sale import SaleItem
    from app.models.stock import StockLevel, StockMovement


class Product(Base):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    barcode: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str]
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"))
    image_url: Mapped[str | None]
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped["Category"] = relationship(back_populates="products")
    prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    stock_level: Mapped["StockLevel | None"] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    stock_movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    sale_items: Mapped[list["SaleItem"]] = relationship(back_populates="product")
