from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_EXAMPLE_ID = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"


class PaymentMethodCreate(BaseModel):
    """Datos para registrar un nuevo método de pago."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "Yape"}}
    )

    name: str = Field(..., description="Nombre del método de pago", examples=["Efectivo", "Yape", "Plin"])


class PaymentMethodRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"id": _EXAMPLE_ID, "name": "Yape"}},
    )

    id: UUID = Field(..., description="Identificador único del método de pago")
    name: str = Field(..., description="Nombre del método de pago")
