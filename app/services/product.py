from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product import ProductRepository
from app.repositories.product_price import ProductPriceRepository
from app.repositories.stock import StockLevelRepository
from app.schemas.product import (
    ProductBarcodeRead,
    ProductCreate,
    ProductRead,
    ProductReadWithCategory,
    ProductUpdate,
)


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ProductRepository(session)
        self.price_repo = ProductPriceRepository(session)
        self.stock_repo = StockLevelRepository(session)

    async def get_by_id(self, id: UUID) -> ProductReadWithCategory:
        product = await self.repo.get_by_id_with_category(id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
            )
        return ProductReadWithCategory.model_validate(product)

    async def get_by_barcode(self, barcode: str) -> ProductBarcodeRead:
        product = await self.repo.get_by_barcode(barcode)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
            )
        price = await self.price_repo.get_current(product.id)
        stock = await self.stock_repo.get_by_product(product.id)
        return ProductBarcodeRead(
            id=product.id,
            barcode=product.barcode,
            name=product.name,
            image_url=product.image_url,
            min_stock=product.min_stock,
            is_active=product.is_active,
            selling_price=price.selling_price if price else None,
            stock=stock.quantity if stock else 0,
        )

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
