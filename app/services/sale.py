from decimal import (
    Decimal,  # Por precisión, se está trabajando con montos de dinero
)
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sale import SaleItem, SalesTransaction, TransactionStatus
from app.repositories.payment_method import PaymentMethodRepository
from app.repositories.product import ProductRepository
from app.repositories.product_price import ProductPriceRepository
from app.repositories.sale import SalesTransactionRepository
from app.repositories.stock import StockLevelRepository
from app.schemas.sale import (
    SalesTransactionCreate,
    SalesTransactionRead,
    SalesTransactionStatusUpdate,
)


class SaleService:
    def __init__(self, session: AsyncSession) -> None:
        self.tx_repo = SalesTransactionRepository(session)
        self.payment_repo = PaymentMethodRepository(session)
        self.product_repo = ProductRepository(session)
        self.price_repo = ProductPriceRepository(session)
        self.stock_repo = StockLevelRepository(session)
        self.session = session

    async def get_all(self) -> list[SalesTransactionRead]:
        transactions = await self.tx_repo.get_all_with_details()
        return [SalesTransactionRead.model_validate(t) for t in transactions]

    async def get_by_id(self, id: UUID) -> SalesTransactionRead:
        transaction = await self.tx_repo.get_by_id_with_details(id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada",
            )
        return SalesTransactionRead.model_validate(transaction)

    async def create_sale(self, data: SalesTransactionCreate) -> SalesTransactionRead:
        payment_method = await self.payment_repo.get_by_id(data.payment_method_id)
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Método de pago no encontrado",
            )

        resolved_items = []
        total_amount = Decimal("0")

        for item in data.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto {item.product_id} no encontrado",
                )
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El producto '{product.name}' no está disponible para la venta",
                )

            price = await self.price_repo.get_current(item.product_id)
            if not price:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El producto '{product.name}' no tiene precio registrado",
                )

            stock = await self.stock_repo.get_by_product(item.product_id)
            available = stock.quantity if stock else 0
            if available < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stock insuficiente para '{product.name}'. Disponible: {available}, solicitado: {item.quantity}",
                )

            subtotal = price.selling_price * item.quantity
            total_amount += subtotal
            resolved_items.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": price.selling_price,
                    "subtotal": subtotal,
                    "product_name_snapshot": product.name,
                }
            )

        CENTS = Decimal("0.01")  # Precisión de 2 decimales
        if total_amount.quantize(CENTS) != data.total_amount.quantize(CENTS):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El total enviado ({data.total_amount}) no coincide con el calculado ({total_amount})",
            )

        transaction = SalesTransaction(
            payment_method=data.payment_method_id,
            total_amount=total_amount,
            status=TransactionStatus.COMPLETED,
        )
        self.session.add(transaction)
        await self.session.flush()

        for item_data in resolved_items:
            self.session.add(SaleItem(transaction_id=transaction.id, **item_data))
            await self.stock_repo.apply_delta(
                item_data["product_id"], -item_data["quantity"]
            )

        await self.session.commit()
        return await self.get_by_id(transaction.id)

    async def update_status(
        self, id: UUID, data: SalesTransactionStatusUpdate
    ) -> SalesTransactionRead:
        transaction = await self.tx_repo.get_by_id(id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada",
            )
        if transaction.status == TransactionStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La transacción ya está cancelada",
            )
        transaction.status = data.status
        await self.session.commit()
        return await self.get_by_id(id)
