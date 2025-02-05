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
    async def test_account_1_not_found(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        account_repository: AccountsRepository,
        make_account: Callable[..., Account],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account_2 = make_account(customer_id=customer.id)
        await account_repository.save_account(account_2)

        payload = {"account_id": str(account_2.id), "amount": 100}

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
                f"/dummy-bank/v1/accounts/{uuid.uuid4()}/transfer", json=payload
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "account not found"}

    @pytest.mark.asyncio
    async def test_account_2_not_found(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        account_repository: AccountsRepository,
        make_account: Callable[..., Account],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account_1 = make_account(customer_id=customer.id)
        await account_repository.save_account(account_1)

        payload = {"account_id": str(uuid.uuid4()), "amount": 100}

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
                f"/dummy-bank/v1/accounts/{account_1.id}/transfer", json=payload
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "account not found"}

    @pytest.mark.asyncio
    async def test_customer_both_customers_not_found(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        account_repository: AccountsRepository,
        make_account: Callable[..., Account],
    ) -> None:
        payload = {"amount": 102.99, "account_id": str(uuid.uuid4())}

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
                f"/dummy-bank/v1/accounts/{uuid.uuid4()}/transfer", json=payload
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "account not found"}


class TestTransferBalance:
    @pytest.mark.asyncio
    async def test(
        self,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=100.50, customer_id=customer.id)
        await account_repository.save_account(account)

        account_2 = make_account(customer_id=customer.id, account_balance=94.27)
        await account_repository.save_account(account_2)

        payload = {"amount": 7.87, "account_id": str(account_2.id)}

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
                f"/dummy-bank/v1/accounts/{account.id}/transfer", json=payload
            )
            assert response.status_code == 200
            assert response.json()[0]["account_balance"] == 9263
            assert response.json()[1]["account_balance"] == 10214

    @pytest.mark.asyncio
    async def test_transfer_more_than_balance(
        self,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(account_balance=100.50, customer_id=customer.id)
        await account_repository.save_account(account)

        account_2 = make_account(customer_id=customer.id, account_balance=94.27)
        await account_repository.save_account(account_2)

        payload = {"amount": 1000, "account_id": str(account_2.id)}

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
                f"/dummy-bank/v1/accounts/{account.id}/transfer", json=payload
            )
            assert response.status_code == 400
            assert (
                response.json()["detail"] == "insufficient funds for this transaction"
            )

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
                f"/dummy-bank/v1/accounts/{uuid.uuid4()}/transfer", json=payload
            )
            assert response.status_code == 422
