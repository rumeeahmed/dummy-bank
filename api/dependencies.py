from collections.abc import Iterator
from typing import Annotated

import structlog
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine

from repository import (
    AccountsRepository,
    AddressesRepository,
    CustomerRepository,
    Repository,
)

from .lock_manager import LockManager
from .settings import Settings


def get_settings(request: Request) -> Settings:
    return request.state._settings


def get_logger(request: Request) -> structlog.stdlib.BoundLogger:
    return request.state._logger


def get_database_engine(request: Request) -> AsyncEngine:
    return request.state._database_engine


def get_repository(
    engine: Annotated[AsyncEngine, Depends(get_database_engine)],
) -> Iterator[Repository]:
    yield Repository(engine=engine)


def get_customer_repository(
    engine: Annotated[AsyncEngine, Depends(get_database_engine)],
) -> Iterator[CustomerRepository]:
    yield CustomerRepository(engine=engine)


def get_account_repository(
    engine: Annotated[AsyncEngine, Depends(get_database_engine)],
) -> Iterator[AccountsRepository]:
    yield AccountsRepository(engine=engine)


def get_address_repository(
    engine: Annotated[AsyncEngine, Depends(get_database_engine)],
) -> Iterator[AddressesRepository]:
    yield AddressesRepository(engine=engine)


def get_lock_manager(request: Request) -> Settings:
    return request.state._lock_manager


SettingsDep = Annotated[Settings, Depends(get_settings)]
LoggerDep = Annotated[structlog.stdlib.BoundLogger, Depends(get_logger)]
DatabaseEngineDep = Annotated[AsyncEngine, Depends(get_database_engine)]
RepositoryDep = Annotated[Repository, Depends(get_repository)]
CustomerRepositoryDep = Annotated[CustomerRepository, Depends(get_customer_repository)]
AccountRepositoryDep = Annotated[AccountsRepository, Depends(get_account_repository)]
AddressesRepositoryDep = Annotated[AddressesRepository, Depends(get_address_repository)]
LockManagerDep = Annotated[LockManager, Depends(get_lock_manager)]
