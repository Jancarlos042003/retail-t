from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.sale import SalesTransaction


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]

    transactions: Mapped[list["SalesTransaction"]] = relationship(
        back_populates="payment_method_rel"
    )
