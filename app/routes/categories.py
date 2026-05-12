from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["Categorías"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: SessionDep) -> CategoryService:
    return CategoryService(session)


ServiceDep = Annotated[CategoryService, Depends(get_service)]


@router.get("/", response_model=list[CategoryRead])
async def list_categories(service: ServiceDep) -> list[CategoryRead]:
    return await service.get_all()


@router.get("/{id}", response_model=CategoryRead)
async def get_category(id: UUID, service: ServiceDep) -> CategoryRead:
    return await service.get_by_id(id)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, service: ServiceDep) -> CategoryRead:
    return await service.create(data)


@router.patch("/{id}", response_model=CategoryRead)
async def update_category(id: UUID, data: CategoryUpdate, service: ServiceDep) -> CategoryRead:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: UUID, service: ServiceDep) -> None:
    await service.delete(id)
