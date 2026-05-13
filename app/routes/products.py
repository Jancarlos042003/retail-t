from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.infrastructure.storage.gcs import GCSStorageBackend
from app.schemas.product import (
    ProductBarcodeRead,
    ProductCreate,
    ProductListResponse,
    ProductRead,
    ProductReadWithCategory,
    ProductUpdate,
)
from app.services.product import ProductService
from app.services.storage import BUCKET_NAME, StorageService

router = APIRouter(prefix="/products", tags=["Productos"])

type SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_service(session: SessionDep) -> ProductService:
    return ProductService(session)


type ServiceDep = Annotated[ProductService, Depends(get_service)]


def get_storage_service() -> StorageService:
    return StorageService(backend=GCSStorageBackend(bucket=BUCKET_NAME))


@router.get("/", response_model=ProductListResponse)
async def list_products(
    service: ServiceDep,
    name: Annotated[str | None, Query(description="Búsqueda por nombre (parcial, sin distinción de mayúsculas)")] = None,
    category_id: Annotated[UUID | None, Query(description="Filtrar por ID de categoría")] = None,
    is_active: Annotated[bool | None, Query(description="Filtrar por estado activo/inactivo")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo de resultados por página (default 25)")] = 25,
    offset: Annotated[int, Query(ge=0, description="Desplazamiento para paginación")] = 0,
) -> ProductListResponse:
    return await service.get_all(
        name=name,
        category_id=category_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@router.get("/barcode/{barcode}", response_model=ProductBarcodeRead)
async def get_product_by_barcode(
    barcode: str, service: ServiceDep
) -> ProductBarcodeRead:
    return await service.get_by_barcode(barcode)


@router.get("/{id}", response_model=ProductReadWithCategory)
async def get_product(id: UUID, service: ServiceDep) -> ProductReadWithCategory:
    return await service.get_by_id(id)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    service: ServiceDep,
    storage: Annotated[StorageService, Depends(get_storage_service)],
    barcode: Annotated[str, Form()],
    name: Annotated[str, Form()],
    category_id: Annotated[UUID, Form()],
    min_stock: Annotated[int, Form(ge=0)] = 0,
    is_active: Annotated[bool, Form()] = True,
    image: Annotated[UploadFile | None, File()] = None,
) -> ProductRead:
    image_url = await storage.upload_image(image) if image is not None else None

    data = ProductCreate(
        barcode=barcode,
        name=name,
        category_id=category_id,
        min_stock=min_stock,
        is_active=is_active,
        image_url=image_url,
    )
    return await service.create(data)


@router.patch("/{id}", response_model=ProductReadWithCategory)
async def update_product(
    id: UUID, data: ProductUpdate, service: ServiceDep
) -> ProductReadWithCategory:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: UUID, service: ServiceDep) -> None:
    await service.delete(id)
