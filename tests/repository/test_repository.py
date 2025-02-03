from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from repository import Repository
from repository.db_customer import DBCustomer


class TestRepositoryEngine:
    def test_get(self) -> None:
        engine = Mock(spec=AsyncEngine)
        repository = Repository(engine=engine)
        assert repository.engine == engine

    def test_is_read_only(self) -> None:
        repository = Repository(engine=Mock(spec=AsyncEngine))
        with pytest.raises(AttributeError):
            repository.engine = Mock(spec=AsyncEngine)  # type: ignore[misc]


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy(self, database_engine: AsyncEngine) -> None:
        repository = Repository(engine=database_engine)
        response = await repository.health_check()
        assert response == "ok"

    @pytest.mark.asyncio
    async def test_unhealthy(self) -> None:
        url = URL.create(
            "postgresql+asyncpg",
            username="bad_username",
            password="bad_password",
            host="bad_host",
            database="bad_database",
        )
        engine = create_async_engine(url, poolclass=NullPool)
        repository = Repository(engine=engine)
        with pytest.raises(Exception):
            await repository.health_check()


class TestGetCount:
    @pytest.mark.asyncio
    async def test(self) -> None:
        mock_result = Mock()
        mock_result.scalar_one.return_value = 10

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_session.__aenter__.return_value = mock_session

        with patch.object(Repository, "_session", return_value=mock_session):
            repo = Repository(engine=MagicMock())
            count = await repo.get_count(DBCustomer)

            mock_session.execute.assert_called_once()
            assert count == 10
