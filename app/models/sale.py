from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.payment_method import PaymentMethod
    from app.models.product import Product


class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payment_method: Mapped[UUID] = mapped_column(ForeignKey("payment_methods.id"))
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus), default=TransactionStatus.PENDING
    )

    payment_method_rel: Mapped["PaymentMethod"] = relationship(
        back_populates="transactions"
    )
    items: Mapped[list["SaleItem"]] = relationship(back_populates="transaction")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(ForeignKey("sales_transactions.id"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    product_name_snapshot: Mapped[str]

    transaction: Mapped["SalesTransaction"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="sale_items")
