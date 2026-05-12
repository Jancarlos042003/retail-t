from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import MovementOperation
from app.repositories.product import ProductRepository
from app.repositories.stock import MovementTypeRepository, StockLevelRepository, StockMovementRepository
from app.schemas.stock import MovementTypeRead, StockLevelRead, StockMovementCreate, StockMovementRead


class StockService:
    def __init__(self, session: AsyncSession) -> None:
        self.movement_type_repo = MovementTypeRepository(session)
        self.stock_level_repo = StockLevelRepository(session)
        self.movement_repo = StockMovementRepository(session)
        self.product_repo = ProductRepository(session)
        self.session = session

    async def get_movement_types(self) -> list[MovementTypeRead]:
        types = await self.movement_type_repo.get_all()
        return [MovementTypeRead.model_validate(t) for t in types]

    async def get_stock_level(self, product_id: UUID) -> StockLevelRead:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        stock = await self.stock_level_repo.get_by_product(product_id)
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto no tiene movimientos de stock registrados",
            )
        return StockLevelRead.model_validate(stock)

    async def get_movement_history(self, product_id: UUID) -> list[StockMovementRead]:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        movements = await self.movement_repo.get_history(product_id)
        return [StockMovementRead.model_validate(m) for m in movements]

    async def register_movement(self, data: StockMovementCreate) -> StockMovementRead:
        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        movement_type = await self.movement_type_repo.get_by_id(data.type_id)
        if not movement_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de movimiento no encontrado")

        delta = data.quantity if movement_type.operation == MovementOperation.IN else -data.quantity

        if movement_type.operation == MovementOperation.OUT:
            current_stock = await self.stock_level_repo.get_by_product(data.product_id)
            current_qty = current_stock.quantity if current_stock else 0
            if current_qty < data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stock insuficiente. Disponible: {current_qty}, solicitado: {data.quantity}",
                )

        await self.stock_level_repo.apply_delta(data.product_id, delta)
        movement = await self.movement_repo.create_movement(data)
        await self.session.commit()
        await self.session.refresh(movement)
        return StockMovementRead.model_validate(movement)
