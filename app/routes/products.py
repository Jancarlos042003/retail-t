from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductReadWithCategory, ProductUpdate
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["Productos"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: SessionDep) -> ProductService:
    return ProductService(session)


ServiceDep = Annotated[ProductService, Depends(get_service)]


@router.get("/", response_model=list[ProductReadWithCategory])
async def list_products(
    service: ServiceDep,
    is_active: Annotated[bool | None, Query(description="Filtrar por estado activo/inactivo")] = None,
) -> list[ProductReadWithCategory]:
    return await service.get_all(is_active=is_active)


@router.get("/{id}", response_model=ProductReadWithCategory)
async def get_product(id: UUID, service: ServiceDep) -> ProductReadWithCategory:
    return await service.get_by_id(id)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, service: ServiceDep) -> ProductRead:
    return await service.create(data)


@router.patch("/{id}", response_model=ProductReadWithCategory)
async def update_product(id: UUID, data: ProductUpdate, service: ServiceDep) -> ProductReadWithCategory:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: UUID, service: ServiceDep) -> None:
    await service.delete(id)
