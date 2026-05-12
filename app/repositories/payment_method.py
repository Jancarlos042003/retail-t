from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_method import PaymentMethod
from app.repositories.base import BaseRepository
from app.schemas.payment_method import PaymentMethodCreate


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PaymentMethod, session)

    async def create(self, data: PaymentMethodCreate) -> PaymentMethod:
        method = PaymentMethod(**data.model_dump())
        self.session.add(method)
        await self.session.commit()
        await self.session.refresh(method)
        return method
