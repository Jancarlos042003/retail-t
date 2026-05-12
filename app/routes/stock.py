from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.stock import MovementTypeRead, StockLevelRead, StockMovementCreate, StockMovementRead
from app.services.stock import StockService

router = APIRouter(prefix="/stock", tags=["Stock"])

type SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: SessionDep) -> StockService:
    return StockService(session)


type ServiceDep = Annotated[StockService, Depends(get_service)]


@router.get("/movement-types", response_model=list[MovementTypeRead])
async def list_movement_types(service: ServiceDep) -> list[MovementTypeRead]:
    return await service.get_movement_types()


@router.get("/{product_id}", response_model=StockLevelRead)
async def get_stock_level(product_id: UUID, service: ServiceDep) -> StockLevelRead:
    return await service.get_stock_level(product_id)


@router.get("/{product_id}/movements", response_model=list[StockMovementRead])
async def get_movement_history(product_id: UUID, service: ServiceDep) -> list[StockMovementRead]:
    return await service.get_movement_history(product_id)


@router.post("/movements", response_model=StockMovementRead, status_code=201)
async def register_movement(data: StockMovementCreate, service: ServiceDep) -> StockMovementRead:
    return await service.register_movement(data)
