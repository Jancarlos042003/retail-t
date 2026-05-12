from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_EXAMPLE_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


class CategoryCreate(BaseModel):
    """Datos requeridos para crear una nueva categoría."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "Bebidas"}}
    )

    name: str = Field(..., description="Nombre de la categoría", examples=["Bebidas", "Snacks", "Lácteos"])


class CategoryUpdate(BaseModel):
    """Campos a actualizar. Solo se modifican los campos enviados."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "Bebidas Frías"}}
    )

    name: str | None = Field(None, description="Nuevo nombre de la categoría", examples=["Bebidas Frías"])


class CategoryRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"id": _EXAMPLE_ID, "name": "Bebidas"}},
    )

    id: UUID = Field(..., description="Identificador único de la categoría", examples=[_EXAMPLE_ID])
    name: str = Field(..., description="Nombre de la categoría", examples=["Bebidas"])
