from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.sale import TransactionStatus
from app.schemas.payment_method import PaymentMethodRead

_TX_ID = "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a"
_PRODUCT_ID = "8a4f2b91-3c7d-4e5f-a6b8-9d0e1f2a3b4c"
_PAYMENT_ID = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
_ITEM_ID = "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b"


class SaleItemCreate(BaseModel):
    product_id: UUID = Field(..., description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad a vender", examples=[3])


class SalesTransactionCreate(BaseModel):
    """Registra una nueva venta. Calcula precios, subtotales y actualiza el stock automáticamente."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_method_id": _PAYMENT_ID,
                "total_amount": 7.50,
                "items": [
                    {"product_id": _PRODUCT_ID, "quantity": 3},
                ],
            }
        }
    )

    payment_method_id: UUID = Field(..., description="ID del método de pago utilizado")
    total_amount: Decimal = Field(..., gt=0, description="Total calculado por el cliente (se verifica contra el cálculo del servidor)")
    items: list[SaleItemCreate] = Field(..., min_length=1, description="Productos de la venta (mínimo 1)")


class SalesTransactionStatusUpdate(BaseModel):
    """Actualiza el estado de una transacción."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"status": "CANCELLED"}}
    )

    status: TransactionStatus = Field(..., description="Nuevo estado de la transacción")


class SaleItemRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": _ITEM_ID,
                "transaction_id": _TX_ID,
                "product_id": _PRODUCT_ID,
                "quantity": 3,
                "unit_price": 2.50,
                "subtotal": 7.50,
                "product_name_snapshot": "Inca Kola 500ml",
            }
        },
    )

    id: UUID = Field(..., description="Identificador único del ítem")
    transaction_id: UUID = Field(..., description="ID de la transacción")
    product_id: UUID = Field(..., description="ID del producto")
    quantity: int = Field(..., description="Cantidad vendida")
    unit_price: Decimal = Field(..., description="Precio unitario al momento de la venta")
    subtotal: Decimal = Field(..., description="Subtotal del ítem (quantity × unit_price)")
    product_name_snapshot: str = Field(..., description="Nombre del producto al momento de la venta")


class SalesTransactionRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": _TX_ID,
                "transaction_date": "2026-05-12T10:00:00Z",
                "total_amount": 7.50,
                "status": "COMPLETED",
                "payment_method_rel": {"id": _PAYMENT_ID, "name": "Yape"},
                "items": [
                    {
                        "id": _ITEM_ID,
                        "transaction_id": _TX_ID,
                        "product_id": _PRODUCT_ID,
                        "quantity": 3,
                        "unit_price": 2.50,
                        "subtotal": 7.50,
                        "product_name_snapshot": "Inca Kola 500ml",
                    }
                ],
            }
        },
    )

    id: UUID = Field(..., description="Identificador único de la transacción")
    transaction_date: datetime = Field(..., description="Fecha y hora de la venta")
    total_amount: Decimal = Field(..., description="Monto total de la venta")
    status: TransactionStatus = Field(..., description="Estado de la transacción")
    payment_method_rel: PaymentMethodRead = Field(..., description="Método de pago utilizado")
    items: list[SaleItemRead] = Field(..., description="Ítems de la venta")
