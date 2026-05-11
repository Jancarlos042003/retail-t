from google.cloud import storage

from app.services.storage.base import StorageService


class GCSStorageService(StorageService):
    def __init__(self, bucket: str):
        self._client = storage.Client()
        self._bucket = bucket

    def upload(self, data: bytes, destination: str) -> str:
        bucket = self._client.bucket(self._bucket)
        blob = bucket.blob(destination)
        blob.upload_from_string(data)
        return destination

    def download(self, source: str) -> bytes:
        bucket = self._client.bucket(self._bucket)
        return bucket.blob(source).download_as_bytes()
