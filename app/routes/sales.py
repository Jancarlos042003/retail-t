from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.sale import SalesTransactionCreate, SalesTransactionRead, SalesTransactionStatusUpdate
from app.services.sale import SaleService

router = APIRouter(prefix="/sales", tags=["Ventas"])

type SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: SessionDep) -> SaleService:
    return SaleService(session)


type ServiceDep = Annotated[SaleService, Depends(get_service)]


@router.get("/", response_model=list[SalesTransactionRead])
async def list_sales(service: ServiceDep) -> list[SalesTransactionRead]:
    return await service.get_all()


@router.get("/{id}", response_model=SalesTransactionRead)
async def get_sale(id: UUID, service: ServiceDep) -> SalesTransactionRead:
    return await service.get_by_id(id)


@router.post("/", response_model=SalesTransactionRead, status_code=status.HTTP_201_CREATED)
async def create_sale(data: SalesTransactionCreate, service: ServiceDep) -> SalesTransactionRead:
    return await service.create_sale(data)


@router.patch("/{id}/status", response_model=SalesTransactionRead)
async def update_sale_status(
    id: UUID, data: SalesTransactionStatusUpdate, service: ServiceDep
) -> SalesTransactionRead:
    return await service.update_status(id, data)
