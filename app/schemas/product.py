from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryRead

_PRODUCT_ID = "8a4f2b91-3c7d-4e5f-a6b8-9d0e1f2a3b4c"
_CATEGORY_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


class ProductCreate(BaseModel):
    """Datos requeridos para registrar un nuevo producto."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "barcode": "7501234567890",
                "name": "Inca Kola 500ml",
                "category_id": _CATEGORY_ID,
                "image_url": "https://storage.googleapis.com/bodega/inca-kola-500ml.jpg",
                "min_stock": 12,
                "is_active": True,
            }
        }
    )

    barcode: str = Field(..., description="Código de barras único del producto", examples=["7501234567890"])
    name: str = Field(..., description="Nombre del producto", examples=["Inca Kola 500ml"])
    category_id: UUID = Field(..., description="ID de la categoría a la que pertenece", examples=[_CATEGORY_ID])
    image_url: str | None = Field(None, description="URL de la imagen en Google Cloud Storage")
    min_stock: int = Field(0, ge=0, description="Stock mínimo antes de emitir alerta", examples=[12])
    is_active: bool = Field(True, description="Si el producto está disponible para la venta")


class ProductUpdate(BaseModel):
    """Campos a actualizar. Solo se modifican los campos enviados."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Inca Kola 500ml Light",
                "min_stock": 24,
                "is_active": True,
            }
        }
    )

    barcode: str | None = Field(None, description="Nuevo código de barras", examples=["7501234567891"])
    name: str | None = Field(None, description="Nuevo nombre del producto", examples=["Inca Kola 500ml Light"])
    category_id: UUID | None = Field(None, description="Nueva categoría del producto")
    image_url: str | None = Field(None, description="Nueva URL de imagen")
    min_stock: int | None = Field(None, ge=0, description="Nuevo stock mínimo", examples=[24])
    is_active: bool | None = Field(None, description="Activar o desactivar el producto")


class ProductRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": _PRODUCT_ID,
                "barcode": "7501234567890",
                "name": "Inca Kola 500ml",
                "category_id": _CATEGORY_ID,
                "image_url": "https://storage.googleapis.com/bodega/inca-kola-500ml.jpg",
                "min_stock": 12,
                "is_active": True,
                "created_at": "2026-05-12T10:00:00Z",
                "updated_at": "2026-05-12T10:00:00Z",
            }
        },
    )

    id: UUID = Field(..., description="Identificador único del producto", examples=[_PRODUCT_ID])
    barcode: str = Field(..., description="Código de barras del producto", examples=["7501234567890"])
    name: str = Field(..., description="Nombre del producto", examples=["Inca Kola 500ml"])
    category_id: UUID = Field(..., description="ID de la categoría", examples=[_CATEGORY_ID])
    image_url: str | None = Field(None, description="URL de la imagen en Google Cloud Storage")
    min_stock: int = Field(..., description="Stock mínimo configurado", examples=[12])
    is_active: bool = Field(..., description="Si el producto está disponible para la venta")
    created_at: datetime = Field(..., description="Fecha de creación del registro")
    updated_at: datetime = Field(..., description="Fecha de última actualización")


class ProductReadWithCategory(ProductRead):
    """Producto con información de su categoría anidada."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": _PRODUCT_ID,
                "barcode": "7501234567890",
                "name": "Inca Kola 500ml",
                "category_id": _CATEGORY_ID,
                "image_url": "https://storage.googleapis.com/bodega/inca-kola-500ml.jpg",
                "min_stock": 12,
                "is_active": True,
                "created_at": "2026-05-12T10:00:00Z",
                "updated_at": "2026-05-12T10:00:00Z",
                "category": {"id": _CATEGORY_ID, "name": "Bebidas"},
            }
        },
    )

    category: CategoryRead = Field(..., description="Información de la categoría del producto")
