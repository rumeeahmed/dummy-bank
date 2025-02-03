from typing import Literal, Type

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Repository:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def health_check(self) -> Literal["ok"]:
        """
        Check if the database connection is alive and healthy.
        """
        async with self.engine.connect() as conn:
            await conn.execute(text("select 1"))

        return "ok"

    def _session(self) -> AsyncSession:
        return async_sessionmaker(self.engine)()

    async def get_count(self, model: Type[DeclarativeBase]) -> int:
        async with self._session() as session:
            result = await session.execute(select(func.count()).select_from(model))
            total_count = result.scalar_one()

        return total_count
