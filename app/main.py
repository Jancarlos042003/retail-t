from fastapi import FastAPI

import app.models.registry  # noqa: F401 - registers all models with SQLAlchemy
from app.routes import categories, product_prices, products, storage

app = FastAPI()

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_prices.router)
app.include_router(storage.router)
