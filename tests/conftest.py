import os
import uuid
from typing import Any, AsyncIterator, Generator
from unittest.mock import Mock

import pytest
import structlog
from dotenv import load_dotenv
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from psycopg import Connection
from pytest_postgresql import factories
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from structlog.stdlib import BoundLogger

from dummy_bank.api.dependencies import (
    get_account_repository,
    get_customer_repository,
    get_database_engine,
    get_lock_manager,
    get_logger,
    get_settings,
)
from dummy_bank.api.lock_manager import LockManager
from dummy_bank.api.main import create_app
from dummy_bank.api.settings import Settings
from dummy_bank.lib.geolocation_client import GoogleMapsClient
from dummy_bank.lib.http_client import BaseHTTPClient
from dummy_bank.repository import (
    AccountsRepository,
    AddressesRepository,
    CustomerRepository,
)

pytest_plugins = [
    "tests.make_domain_objects",
]

_PYTEST_WORKER = os.getenv("PYTEST_XDIST_WORKER", "master")
_TEST_DB_NAME = f"dummy_bank_{_PYTEST_WORKER}"


def load_schema(
    *,
    host: str,
    port: int,
    user: str,
    dbname: str,
    password: str,
) -> None:
    from sqlalchemy import create_engine

    from dummy_bank.repository import Base

    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    engine.dispose()


postgresql_proc = factories.postgresql_proc(
    user="service",
    password="service",
    host="127.0.0.1",
    dbname="postgres",
    load=[load_schema],
)

postgresql = factories.postgresql("postgresql_proc", dbname=_TEST_DB_NAME)


@pytest.fixture
async def database_engine(postgresql: Connection) -> AsyncIterator[AsyncEngine]:
    url = URL.create(
        "postgresql+asyncpg",
        username=postgresql.info.user,
        password=postgresql.info.password,
        host=postgresql.info.host,
        port=postgresql.info.port,
        database=postgresql.info.dbname,
    )
    engine = create_async_engine(url, pool_size=5, max_overflow=10)

    yield engine

    await engine.dispose()


@pytest.fixture
def app(
    database_engine: AsyncEngine,
    customer_repository: CustomerRepository,
    lock_manager: LockManager,
    account_repository: AccountsRepository,
    logger: BoundLogger,
    settings: Settings,
) -> FastAPI:
    def override_get_customer_repository() -> CustomerRepository:
        return customer_repository

    def override_get_account_repository() -> AccountsRepository:
        return account_repository

    def override_get_lock_manager() -> LockManager:
        return lock_manager

    def override_get_logger() -> BoundLogger:
        return logger

    def override_get_settings() -> Settings:
        return settings

    def override_get_database_engine() -> AsyncEngine:
        return database_engine

    app = create_app(settings=Settings(), logger=Mock())
    app.dependency_overrides[get_customer_repository] = override_get_customer_repository
    app.dependency_overrides[get_account_repository] = override_get_account_repository
    app.dependency_overrides[get_lock_manager] = override_get_lock_manager
    app.dependency_overrides[get_logger] = override_get_logger
    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_database_engine] = override_get_database_engine

    return app


@pytest.fixture
async def test_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def load_env_vars() -> None:
    project_root = os.path.abspath(os.path.dirname(__file__))
    env_path = os.path.join(project_root, "..", ".env")

    if os.path.isfile(env_path):
        load_dotenv(dotenv_path=env_path, override=True)


@pytest.fixture
async def customer_repository(database_engine: AsyncEngine) -> CustomerRepository:
    return CustomerRepository(engine=database_engine)


@pytest.fixture
async def account_repository(database_engine: AsyncEngine) -> AccountsRepository:
    return AccountsRepository(engine=database_engine)


@pytest.fixture
async def addresses_repository(database_engine: AsyncEngine) -> AddressesRepository:
    return AddressesRepository(engine=database_engine)


@pytest.fixture
async def settings() -> Settings:
    return Settings()


@pytest.fixture
async def logger() -> BoundLogger:
    return structlog.get_logger()


@pytest.fixture()
def base_http_client(base_url: str) -> BaseHTTPClient:
    return BaseHTTPClient(base_url=base_url)


@pytest.fixture()
def google_maps_url() -> str:
    return "https://maps.dummy.com"


@pytest.fixture()
def google_maps_api_key() -> str:
    return "dummy_secret"


@pytest.fixture()
def lock_manager() -> Generator[LockManager, Any, None]:
    yield LockManager()


@pytest.fixture()
def lock_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture()
def google_maps_client(
    google_maps_url: str, google_maps_api_key: str
) -> GoogleMapsClient:
    return GoogleMapsClient(base_url=google_maps_url, api_key=google_maps_api_key)


@pytest.fixture()
def base_url() -> str:
    return "https://dummy-bank.co.uk"


@pytest.fixture()
def google_maps_response() -> dict:
    return {
        "results": [
            {
                "address_components": [
                    {
                        "long_name": "146",
                        "short_name": "146",
                        "types": ["street_number"],
                    },
                    {
                        "long_name": "Putteridge Road",
                        "short_name": "Putteridge Rd",
                        "types": ["route"],
                    },
                    {
                        "long_name": "Luton",
                        "short_name": "Luton",
                        "types": ["postal_town"],
                    },
                    {
                        "long_name": "Luton",
                        "short_name": "Luton",
                        "types": ["administrative_area_level_2", "political"],
                    },
                    {
                        "long_name": "England",
                        "short_name": "England",
                        "types": ["administrative_area_level_1", "political"],
                    },
                    {
                        "long_name": "United Kingdom",
                        "short_name": "GB",
                        "types": ["country", "political"],
                    },
                    {
                        "long_name": "LU2 8HQ",
                        "short_name": "LU2 8HQ",
                        "types": ["postal_code"],
                    },
                ],
                "formatted_address": "146 Putteridge Rd, Luton LU2 8HQ, UK",
                "geometry": {
                    "location": {"lat": 51.9038061, "lng": -0.3852515},
                    "location_type": "ROOFTOP",
                    "viewport": {
                        "northeast": {
                            "lat": 51.90517183029149,
                            "lng": -0.3839164197084979,
                        },
                        "southwest": {
                            "lat": 51.90247386970849,
                            "lng": -0.386614380291502,
                        },
                    },
                },
                "navigation_points": [
                    {
                        "location": {
                            "latitude": 51.90385089999999,
                            "longitude": -0.3852887,
                        }
                    }
                ],
                "place_id": "ChIJd0_jcNdJdkgRoxxJizMNdV0",
                "plus_code": {
                    "compound_code": "WJ37+GV Luton, UK",
                    "global_code": "9C3XWJ37+GV",
                },
                "types": ["street_address"],
            }
        ],
        "status": "OK",
    }
