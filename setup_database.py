import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database.models import Base

DATABASE_URL = "sqlite+aiosqlite:///./database/web_crawler.db"

async def init_db():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
