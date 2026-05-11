from fastapi import FastAPI

from app.routes import storage

app = FastAPI()

app.include_router(storage.router)
