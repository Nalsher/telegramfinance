from sqlalchemy.ext.asyncio.engine import create_async_engine

url = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"

engine = create_async_engine(url=url,echo=True)
