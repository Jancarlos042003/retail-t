from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

DATABASE_URL = settings.db_url

# Supabase requiere SSL; asyncpg lo recibe como connect_arg, no en la URL
connect_args = {"ssl": "require"} if settings.DATABASE_URL else {}

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=connect_args)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
