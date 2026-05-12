from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import SaleItem, SalesTransaction
from app.repositories.base import BaseRepository


class SalesTransactionRepository(BaseRepository[SalesTransaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SalesTransaction, session)

    async def get_by_id_with_details(self, id: UUID) -> SalesTransaction | None:
        result = await self.session.execute(
            select(SalesTransaction)
            .options(
                selectinload(SalesTransaction.items),
                selectinload(SalesTransaction.payment_method_rel),
            )
            .where(SalesTransaction.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_with_details(self) -> list[SalesTransaction]:
        result = await self.session.execute(
            select(SalesTransaction)
            .options(
                selectinload(SalesTransaction.items),
                selectinload(SalesTransaction.payment_method_rel),
            )
            .order_by(SalesTransaction.transaction_date.desc())
        )
        return list(result.scalars().all())


class SaleItemRepository(BaseRepository[SaleItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SaleItem, session)
