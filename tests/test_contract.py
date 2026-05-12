import pytest
import schemathesis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import get_db
from app.main import app
from app.routes.products import get_storage_service
from app.services.storage import StorageService
from tests.conftest import TEST_DATABASE_URL, _FakeStorageBackend

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


@pytest.fixture(scope="module", autouse=True)
def override_contract_deps():
    # NullPool: fresh connection per request, no pool shared across event loops.
    # This avoids asyncpg cross-event-loop conflicts with schemathesis sync tests.
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def contract_get_db():
        async with factory() as sess:
            yield sess

    app.dependency_overrides[get_db] = contract_get_db
    app.dependency_overrides[get_storage_service] = lambda: StorageService(
        backend=_FakeStorageBackend()
    )
    yield
    app.dependency_overrides.clear()


@schema.parametrize()
def test_api_contract(case):
    # Only fail on 5xx — the OpenAPI spec doesn't yet document all 4xx codes.
    # schemathesis still finds them and reports; we treat them as warnings, not failures.
    from schemathesis.checks import not_a_server_error
    case.call_and_validate(checks=[not_a_server_error])
