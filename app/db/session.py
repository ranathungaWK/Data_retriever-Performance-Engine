from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,
    pool_pre_ping = True,
    pool_size = 10 ,
    max_overflow = 20
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_ = AsyncSession,
    autocommit = False,
    autoflush=False,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()