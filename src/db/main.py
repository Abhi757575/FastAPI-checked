from sqlmodel import SQLModel, create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from src.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    url=Config.DB_CONNECTION,
    echo=True, 
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    async with engine.begin() as conn:
        from src.db.models import Book

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

bind = AsyncEngine
async def get_session() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        yield session
