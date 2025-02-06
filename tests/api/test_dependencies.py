from unittest.mock import Mock

import structlog
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from api.dependencies import (
    AccountRepositoryDep,
    AddressesRepositoryDep,
    CustomerRepositoryDep,
    DatabaseEngineDep,
    LoggerDep,
    RepositoryDep,
    SettingsDep,
    get_database_engine,
)
from api.main import create_app
from api.settings import Settings


class TestGetSettings:
    def test(self) -> None:
        settings = Settings()
        app = create_app(settings, Mock())

        @app.get("/test", status_code=204)
        def fn(settings: SettingsDep) -> None:
            assert settings == settings
            return

        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 204


class TestGetLogger:
    def test(self) -> None:
        logger = structlog.get_logger()
        app = create_app(Settings(), logger)

        @app.get("/test", status_code=204)
        def fn(logger: LoggerDep) -> None:
            assert logger == logger
            return

        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 204


class TestGetDatabaseEngine:
    def test(self) -> None:
        settings = Settings()
        app = create_app(settings, Mock())

        @app.get("/test", status_code=204)
        def fn(database_engine: DatabaseEngineDep) -> None:
            assert database_engine.url == settings.database_url()
            return

        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 204


class TestGetRepository:
    def test(self) -> None:
        app = create_app(Settings(), Mock())

        database_engine = Mock(spec=AsyncEngine)

        def override_get_database_engine(request: Request) -> AsyncEngine:
            return database_engine

        app.dependency_overrides[get_database_engine] = override_get_database_engine

        @app.get("/test", status_code=204)
        def fn(repository: RepositoryDep) -> None:
            assert repository.engine == database_engine
            return

        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 204


class TestGetCustomerRepository:
    def test(self) -> None:
        app = create_app(Settings(), Mock())

        database_engine = Mock(spec=AsyncEngine)

        def override_get_database_engine(request: Request) -> AsyncEngine:
            return database_engine

        app.dependency_overrides[get_database_engine] = override_get_database_engine

        @app.get("/test", status_code=204)
        def fn(customer_repository: CustomerRepositoryDep) -> None:
            assert customer_repository.engine == database_engine
            return

        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 204


class TestGetAccountRepository:
    def test(self) -> None:
        app = create_app(Settings(), Mock())

        database_engine = Mock(spec=AsyncEngine)

        def override_get_database_engine(request: Request) -> AsyncEngine:
            return database_engine

        app.dependency_overrides[get_database_engine] = override_get_database_engine

        @app.get("/test", status_code=204)
        def fn(account_repository: AccountRepositoryDep) -> None:
            assert account_repository.engine == database_engine
            return

        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 204


class TestGetAddressesRepository:
    def test(self) -> None:
        app = create_app(Settings(), Mock())

        database_engine = Mock(spec=AsyncEngine)

        def override_get_database_engine(request: Request) -> AsyncEngine:
            return database_engine

        app.dependency_overrides[get_database_engine] = override_get_database_engine

        @app.get("/test", status_code=204)
        def fn(address_repository: AddressesRepositoryDep) -> None:
            assert address_repository.engine == database_engine
            return

        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 204
