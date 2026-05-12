from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.stock import MovementOperation

_PRODUCT_ID = "8a4f2b91-3c7d-4e5f-a6b8-9d0e1f2a3b4c"
_TYPE_ID = "c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e6f"
_MOVEMENT_ID = "f6e5d4c3-b2a1-0f9e-8d7c-6b5a4d3c2b1a"


class MovementTypeRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": _TYPE_ID,
                "code": "PURCHASE",
                "name": "Compra a proveedor",
                "operation": "IN",
            }
        },
    )

    id: UUID = Field(..., description="Identificador único del tipo de movimiento")
    code: str = Field(..., description="Código único del tipo", examples=["PURCHASE", "SALE", "ADJUSTMENT"])
    name: str = Field(..., description="Nombre descriptivo", examples=["Compra a proveedor"])
    operation: MovementOperation = Field(..., description="Dirección del movimiento: IN suma stock, OUT resta")


class StockLevelRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "product_id": _PRODUCT_ID,
                "quantity": 48,
                "updated_at": "2026-05-12T10:00:00Z",
            }
        },
    )

    product_id: UUID = Field(..., description="ID del producto")
    quantity: int = Field(..., description="Cantidad actual en stock", examples=[48])
    updated_at: datetime = Field(..., description="Fecha del último movimiento")


class StockMovementCreate(BaseModel):
    """Registra un movimiento de stock. Actualiza el nivel de stock automáticamente."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": _PRODUCT_ID,
                "type_id": _TYPE_ID,
                "quantity": 24,
                "reason": "Reposición semanal",
            }
        }
    )

    product_id: UUID = Field(..., description="ID del producto")
    type_id: UUID = Field(..., description="ID del tipo de movimiento")
    quantity: int = Field(..., gt=0, description="Cantidad a mover (siempre positivo)", examples=[24])
    reason: str | None = Field(None, description="Motivo del movimiento", examples=["Reposición semanal"])


class StockMovementRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": _MOVEMENT_ID,
                "product_id": _PRODUCT_ID,
                "type_id": _TYPE_ID,
                "quantity": 24,
                "reason": "Reposición semanal",
                "created_at": "2026-05-12T10:00:00Z",
            }
        },
    )

    id: UUID = Field(..., description="Identificador único del movimiento")
    product_id: UUID = Field(..., description="ID del producto")
    type_id: UUID = Field(..., description="ID del tipo de movimiento")
    quantity: int = Field(..., description="Cantidad movida")
    reason: str | None = Field(None, description="Motivo del movimiento")
    created_at: datetime = Field(..., description="Fecha y hora del movimiento")
