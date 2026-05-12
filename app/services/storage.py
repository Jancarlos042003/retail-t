import uuid

from fastapi import HTTPException, UploadFile, status

from app.infrastructure.storage.base import StorageBackend

BUCKET_NAME = "productos-image"
VALID_EXTENSIONS = {".jpg", ".jpeg", ".webp"}


class StorageService:
    def __init__(self, backend: StorageBackend) -> None:
        self.backend = backend

    async def upload_image(self, file: UploadFile) -> str:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower()

        if ext not in VALID_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensión no válida. Se aceptan: {', '.join(VALID_EXTENSIONS)}",
            )

        filename = f"{uuid.uuid4()}{ext}"
        contents = await file.read()
        self.backend.upload(data=contents, destination=filename)

        return f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
