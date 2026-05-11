import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.services.storage.base import StorageService
from app.services.storage.gcs import GCSStorageService

router = APIRouter(prefix="/storage", tags=["storage"])

BUCKET_NAME = "productos-image"
VALID_EXTENSIONS = {".jpg", ".jpeg", ".webp"}


# Inyeccción de Dependencias
def get_storage_service() -> StorageService:
    return GCSStorageService(bucket=BUCKET_NAME)


@router.post("/upload")
async def upload_image(
    file: UploadFile,
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower()

    if ext not in VALID_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no válida. Se aceptan: {', '.join(VALID_EXTENSIONS)}",
        )

    new_filename = f"{uuid.uuid4()}{ext}"

    contents = await file.read()
    storage_service.upload(data=contents, destination=new_filename)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{new_filename}"

    return {"url": public_url}
