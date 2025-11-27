from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from collections.abc import AsyncGenerator
from app.settings import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    settings.DB_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    future=True,
    pool_size=settings.DB_POOL_SIZE, 
    max_overflow=settings.DB_MAX_OVERFLOW,
)



SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise