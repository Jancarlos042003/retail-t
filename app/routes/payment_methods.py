from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodRead
from app.services.payment_method import PaymentMethodService

router = APIRouter(prefix="/payment-methods", tags=["Métodos de Pago"])

type SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: SessionDep) -> PaymentMethodService:
    return PaymentMethodService(session)


type ServiceDep = Annotated[PaymentMethodService, Depends(get_service)]


@router.get("/", response_model=list[PaymentMethodRead])
async def list_payment_methods(service: ServiceDep) -> list[PaymentMethodRead]:
    return await service.get_all()


@router.get("/{id}", response_model=PaymentMethodRead)
async def get_payment_method(id: UUID, service: ServiceDep) -> PaymentMethodRead:
    return await service.get_by_id(id)


@router.post("/", response_model=PaymentMethodRead, status_code=status.HTTP_201_CREATED)
async def create_payment_method(data: PaymentMethodCreate, service: ServiceDep) -> PaymentMethodRead:
    return await service.create(data)
