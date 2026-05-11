from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    def upload(self, data: bytes, destination: str) -> str: ...

    @abstractmethod
    def download(self, source: str) -> bytes: ...
