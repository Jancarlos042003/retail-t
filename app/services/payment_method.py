from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.payment_method import PaymentMethodRepository
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodRead


class PaymentMethodService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PaymentMethodRepository(session)

    async def get_all(self) -> list[PaymentMethodRead]:
        methods = await self.repo.get_all()
        return [PaymentMethodRead.model_validate(m) for m in methods]

    async def get_by_id(self, id: UUID) -> PaymentMethodRead:
        method = await self.repo.get_by_id(id)
        if not method:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Método de pago no encontrado")
        return PaymentMethodRead.model_validate(method)

    async def create(self, data: PaymentMethodCreate) -> PaymentMethodRead:
        method = await self.repo.create(data)
        return PaymentMethodRead.model_validate(method)
