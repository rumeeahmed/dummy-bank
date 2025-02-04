from typing import Any, AsyncIterator, Callable
from uuid import uuid4

import pytest
import structlog
from psycopg import Connection
from pytest_postgresql import factories
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool
from structlog.stdlib import BoundLogger

from api.settings import Settings
from domain import Account, Customer
from lib.geolocation_client import GoogleMapsClient
from lib.http_client import BaseHTTPClient
from repository import AccountsRepository, Base, CustomerRepository

postgresql_in_docker = factories.postgresql_noproc(
    port=5432, user="service", password="service", dbname="dummy_bank"
)
postgresql = factories.postgresql("postgresql_in_docker", dbname="dummy_bank")


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

    engine = create_async_engine(url, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def customer_repository(database_engine: AsyncEngine) -> CustomerRepository:
    return CustomerRepository(engine=database_engine)


@pytest.fixture
async def account_repository(database_engine: AsyncEngine) -> AccountsRepository:
    return AccountsRepository(engine=database_engine)


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


@pytest.fixture()
def make_customer(**kw: Any) -> Callable[..., Customer]:
    def _make_customer(**kw: Any) -> Customer:
        kwargs: dict = {
            "id": uuid4(),
            "created_at": None,
            "updated_at": None,
            "first_name": "Bob",
            "middle_names": "Bobberson",
            "last_name": "Bobbington",
            "email": None,
            "phone": None,
        }
        return Customer(**{**kwargs, **kw})

    return _make_customer


@pytest.fixture()
def make_account(**kw: Any) -> Callable[..., Account]:
    def _make_account(**kw: Any) -> Account:
        kwargs: dict = {
            "id": uuid4(),
            "customer_id": uuid4(),
            "created_at": None,
            "updated_at": None,
            "account_type": "Current",
            "account_number": "12345",
            "account_balance": 0,
        }
        return Account(**{**kwargs, **kw})

    return _make_account
