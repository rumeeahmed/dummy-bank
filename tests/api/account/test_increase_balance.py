import uuid
from typing import Any, Callable
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_account_repository, get_customer_repository
from api.main import create_app
from api.settings import Settings
from domain import Account, Customer
from repository import AccountsRepository, CustomerRepository


class TestAccountNotFound:
    @pytest.mark.asyncio
    async def test(
        self,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
    ) -> None:
        payload = {"amount": 102.99}

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_account_repository() -> AccountsRepository:
            return account_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )
        app.dependency_overrides[get_account_repository] = (
            override_get_account_repository
        )

        with TestClient(app) as client:
            response = client.post(
                f"/dummy-bank/v1/accounts/{uuid.uuid4()}/deposit", json=payload
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "account not found"}


class TestIncreaseBalance:
    @pytest.mark.asyncio
    async def test(
        self,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        payload = {"amount": 102.99}
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=100.50, customer_id=customer.id)
        await account_repository.save_account(account)

        loaded_customer = await customer_repository.load_customer_with_id(customer.id)
        assert loaded_customer is not None

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_account_repository() -> AccountsRepository:
            return account_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )
        app.dependency_overrides[get_account_repository] = (
            override_get_account_repository
        )

        with TestClient(app) as client:
            response = client.post(
                f"/dummy-bank/v1/accounts/{account.id}/deposit", json=payload
            )
            assert response.status_code == 200
            assert response.json()["account_balance"] == 20349

    @pytest.mark.parametrize(
        argnames=["field", "value"],
        argvalues=[
            ("balance", None),
            ("balance", "remove"),
            ("balance", -12),
        ],
    )
    @pytest.mark.asyncio
    async def test_bad_payload(
        self, customer_repository: CustomerRepository, field: str, value: Any
    ) -> None:
        payload: dict = {}

        if value is not None and value == "remove":
            payload.pop(field, None)
        else:
            payload[field] = value

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )

        with TestClient(app) as client:
            response = client.post(
                f"/dummy-bank/v1/accounts/{uuid.uuid4()}/deposit", json=payload
            )
            assert response.status_code == 422
