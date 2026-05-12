from fastapi import FastAPI

import app.models.registry  # noqa: F401 - registers all models with SQLAlchemy
from app.routes import (
    categories,
    payment_methods,
    product_prices,
    products,
    sales,
    stock,
    storage,
)

app = FastAPI()

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_prices.router)
app.include_router(stock.router)
app.include_router(payment_methods.router)
app.include_router(sales.router)
app.include_router(storage.router)


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {"message": "Bienvenido a la API de Bodega 🏪"}
