from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.product_price import ProductPriceCreate, ProductPriceRead
from app.services.product_price import ProductPriceService

router = APIRouter(prefix="/products/{product_id}/prices", tags=["Precios"])

type SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: SessionDep) -> ProductPriceService:
    return ProductPriceService(session)


type ServiceDep = Annotated[ProductPriceService, Depends(get_service)]


@router.get("/", response_model=list[ProductPriceRead])
async def get_price_history(product_id: UUID, service: ServiceDep) -> list[ProductPriceRead]:
    return await service.get_history(product_id)


@router.get("/current", response_model=ProductPriceRead)
async def get_current_price(product_id: UUID, service: ServiceDep) -> ProductPriceRead:
    return await service.get_current(product_id)


@router.post("/", response_model=ProductPriceRead, status_code=status.HTTP_201_CREATED)
async def set_price(
    product_id: UUID, data: ProductPriceCreate, service: ServiceDep
) -> ProductPriceRead:
    return await service.set_price(product_id, data)
