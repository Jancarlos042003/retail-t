from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
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

    async def get_all(
        self,
        *,
        name: str | None = None,
        category_id: UUID | None = None,
        is_active: bool | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> tuple[list[Product], int]:
        filters = []
        if name is not None:
            filters.append(Product.name.ilike(f"%{name}%"))
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if is_active is not None:
            filters.append(Product.is_active == is_active)

        count_result = await self.session.execute(
            select(func.count(Product.id)).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(*filters)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_by_barcode(self, barcode: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.session.add(product)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Datos inválidos: verifica que la categoría exista",
            )
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
