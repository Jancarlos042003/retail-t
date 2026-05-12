from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import MovementType, StockLevel, StockMovement
from app.repositories.base import BaseRepository
from app.schemas.stock import StockMovementCreate


class MovementTypeRepository(BaseRepository[MovementType]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MovementType, session)

    async def get_by_code(self, code: str) -> MovementType | None:
        result = await self.session.execute(
            select(MovementType).where(MovementType.code == code)
        )
        return result.scalar_one_or_none()


class StockLevelRepository(BaseRepository[StockLevel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(StockLevel, session)

    async def get_by_product(self, product_id: UUID) -> StockLevel | None:
        return await self.session.get(StockLevel, product_id)

    async def apply_delta(self, product_id: UUID, delta: int) -> StockLevel:
        """Suma o resta al stock actual. Crea el registro si no existe. No hace commit."""
        stock = await self.get_by_product(product_id)
        if stock:
            stock.quantity += delta
        else:
            stock = StockLevel(product_id=product_id, quantity=delta)
            self.session.add(stock)
        return stock


class StockMovementRepository(BaseRepository[StockMovement]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(StockMovement, session)

    async def get_history(self, product_id: UUID) -> list[StockMovement]:
        result = await self.session.execute(
            select(StockMovement)
            .where(StockMovement.product_id == product_id)
            .order_by(StockMovement.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_movement(self, data: StockMovementCreate) -> StockMovement:
        """Crea el registro del movimiento. No hace commit."""
        movement = StockMovement(**data.model_dump())
        self.session.add(movement)
        return movement
