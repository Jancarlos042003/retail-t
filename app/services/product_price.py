from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product import ProductRepository
from app.repositories.product_price import ProductPriceRepository
from app.schemas.product_price import ProductPriceCreate, ProductPriceRead


class ProductPriceService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ProductPriceRepository(session)
        self.product_repo = ProductRepository(session)
        self.session = session

    async def _verify_product(self, product_id: UUID) -> None:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    async def get_current(self, product_id: UUID) -> ProductPriceRead:
        await self._verify_product(product_id)
        price = await self.repo.get_current(product_id)
        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto no tiene precio registrado",
            )
        return ProductPriceRead.model_validate(price)

    async def get_history(self, product_id: UUID) -> list[ProductPriceRead]:
        await self._verify_product(product_id)
        prices = await self.repo.get_history(product_id)
        return [ProductPriceRead.model_validate(p) for p in prices]

    async def set_price(self, product_id: UUID, data: ProductPriceCreate) -> ProductPriceRead:
        await self._verify_product(product_id)
        await self.repo.close_current(product_id)
        price = await self.repo.create_price(product_id, data.selling_price)
        await self.session.commit()
        await self.session.refresh(price)
        return ProductPriceRead.model_validate(price)
