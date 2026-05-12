from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_price import ProductPrice
from app.repositories.base import BaseRepository


class ProductPriceRepository(BaseRepository[ProductPrice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ProductPrice, session)

    async def get_current(self, product_id: UUID) -> ProductPrice | None:
        result = await self.session.execute(
            select(ProductPrice)
            .where(ProductPrice.product_id == product_id)
            .where(ProductPrice.effective_to.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_history(self, product_id: UUID) -> list[ProductPrice]:
        result = await self.session.execute(
            select(ProductPrice)
            .where(ProductPrice.product_id == product_id)
            .order_by(ProductPrice.id)
        )
        return list(result.scalars().all())

    async def close_current(self, product_id: UUID) -> None:
        """Cierra el precio vigente. No hace commit — el service lo maneja."""
        await self.session.execute(
            update(ProductPrice)
            .where(ProductPrice.product_id == product_id)
            .where(ProductPrice.effective_to.is_(None))
            .values(effective_to=datetime.now(timezone.utc))
        )

    async def create_price(self, product_id: UUID, selling_price: Decimal) -> ProductPrice:
        """Crea un nuevo registro de precio. No hace commit — el service lo maneja."""
        price = ProductPrice(product_id=product_id, selling_price=selling_price)
        self.session.add(price)
        return price
