from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product import ProductRepository
from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductReadWithCategory,
    ProductUpdate,
)


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ProductRepository(session)

    async def get_by_id(self, id: UUID) -> ProductReadWithCategory:
        product = await self.repo.get_by_id_with_category(id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
            )
        return ProductReadWithCategory.model_validate(product)

    async def get_by_barcode(self, barcode: str) -> ProductReadWithCategory:
        product = await self.repo.get_by_barcode(barcode)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
            )
        return ProductReadWithCategory.model_validate(product)

    async def get_all(
        self, *, is_active: bool | None = None
    ) -> list[ProductReadWithCategory]:
        products = await self.repo.get_all(is_active=is_active)
        return [ProductReadWithCategory.model_validate(p) for p in products]

    async def create(self, data: ProductCreate) -> ProductRead:
        existing = await self.repo.get_by_barcode(data.barcode)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un producto con el código de barras '{data.barcode}'",
            )
        product = await self.repo.create(data)
        return ProductRead.model_validate(product)

    async def update(self, id: UUID, data: ProductUpdate) -> ProductReadWithCategory:
        if data.barcode is not None:
            existing = await self.repo.get_by_barcode(data.barcode)
            if existing and existing.id != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El código de barras '{data.barcode}' ya está en uso",
                )
        product = await self.repo.update(id, data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
            )
        return await self.get_by_id(id)

    async def delete(self, id: UUID) -> None:
        deleted = await self.repo.delete(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
            )
