from fastapi import FastAPI

import app.models.registry  # noqa: F401 - registers all models with SQLAlchemy
from app.routes import storage

app = FastAPI()

app.include_router(storage.router)
