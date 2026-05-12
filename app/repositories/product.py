from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base import BaseRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Product, session)

    async def get_by_id_with_category(self, id: UUID) -> Product | None:
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, *, is_active: bool | None = None) -> list[Product]:
        query = select(Product).options(selectinload(Product.category))
        if is_active is not None:
            query = query.where(Product.is_active == is_active)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_barcode(self, barcode: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, id: UUID, data: ProductUpdate) -> Product | None:
        product = await self.get_by_id(id)
        if not product:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.session.commit()
        await self.session.refresh(product)
        return product
