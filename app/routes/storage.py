from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.infrastructure.storage.gcs import GCSStorageBackend
from app.services.storage import BUCKET_NAME, StorageService

router = APIRouter(prefix="/storage", tags=["storage"])


def get_storage_service() -> StorageService:
    return StorageService(backend=GCSStorageBackend(bucket=BUCKET_NAME))


type StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]


@router.post("/upload")
async def upload_image(
    file: UploadFile,
    storage_service: StorageServiceDep,
) -> dict:
    url = await storage_service.upload_image(file)
    return {"url": url}
