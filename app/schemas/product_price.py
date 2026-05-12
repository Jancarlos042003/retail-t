from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_PRODUCT_ID = "8a4f2b91-3c7d-4e5f-a6b8-9d0e1f2a3b4c"
_PRICE_ID = "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"


class ProductPriceCreate(BaseModel):
    """Establece un nuevo precio para un producto.
    Cierra el precio vigente y crea uno nuevo automáticamente."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"selling_price": 2.50}}
    )

    selling_price: Decimal = Field(
        ..., gt=0, description="Nuevo precio de venta", examples=[2.50]
    )


class ProductPriceRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": _PRICE_ID,
                "product_id": _PRODUCT_ID,
                "selling_price": 2.50,
                "effective_to": None,
            }
        },
    )

    id: UUID = Field(..., description="Identificador único del registro de precio")
    product_id: UUID = Field(..., description="ID del producto al que pertenece")
    selling_price: Decimal = Field(..., description="Precio de venta")
    effective_to: datetime | None = Field(
        None, description="Fecha de cierre del precio. NULL indica que es el precio vigente"
    )
