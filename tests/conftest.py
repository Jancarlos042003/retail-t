from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import get_db
from app.infrastructure.storage.base import StorageBackend
from app.main import app  # also registers all models via app.models.registry
from app.models.base import Base
from app.models.category import Category
from app.models.payment_method import PaymentMethod
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.stock import MovementOperation, MovementType, StockLevel
from app.routes.products import get_storage_service
from app.services.storage import StorageService

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/bodega_test"
)


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(test_engine):
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess
    # Truncate all tables in reverse FK dependency order for isolation
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


class _FakeStorageBackend(StorageBackend):
    def upload(self, data: bytes, destination: str) -> str:
        return f"https://storage.test/{destination}"

    def download(self, source: str) -> bytes:
        return b""


@pytest.fixture
async def client(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage_service] = lambda: StorageService(
        backend=_FakeStorageBackend()
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ── Seed data fixtures ────────────────────────────────────────────────────────


@pytest.fixture
async def category(session):
    cat = Category(name="Bebidas")
    session.add(cat)
    await session.commit()
    return cat


@pytest.fixture
async def payment_method(session):
    pm = PaymentMethod(name="Efectivo")
    session.add(pm)
    await session.commit()
    return pm


@pytest.fixture
async def movement_type_in(session):
    mt = MovementType(
        code="ENTRADA", name="Entrada de mercancía", operation=MovementOperation.IN
    )
    session.add(mt)
    await session.commit()
    return mt


@pytest.fixture
async def movement_type_out(session):
    mt = MovementType(
        code="SALIDA", name="Salida de mercancía", operation=MovementOperation.OUT
    )
    session.add(mt)
    await session.commit()
    return mt


@pytest.fixture
async def product(session, category):
    prod = Product(
        barcode="7501000000001",
        name="Coca Cola 600ml",
        category_id=category.id,
        min_stock=5,
        is_active=True,
    )
    session.add(prod)
    await session.flush()

    stock = StockLevel(product_id=prod.id, quantity=100)
    session.add(stock)

    price = ProductPrice(product_id=prod.id, selling_price=Decimal("15.00"))
    session.add(price)

    await session.commit()
    return prod
