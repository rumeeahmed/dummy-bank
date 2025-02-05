from typing import Any, Callable
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from api.dependencies import get_account_repository, get_customer_repository
from api.main import create_app
from api.settings import Settings
from domain import Customer
from repository import AccountsRepository, CustomerRepository


class TestCreateAccount:
    @patch("api.account.router.uuid4")
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test(
        self,
        mock_uuid: Mock,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        loaded_customer = await customer_repository.load_customer_with_id(customer.id)
        assert loaded_customer is not None

        account_id = UUID("c57a1942-56ed-4e35-87af-2c4241b55149")
        mock_uuid.return_value = account_id

        payload = {
            "account_type": "debit",
            "account_number": "12345",
            "initial_balance": 100,
            "customer_id": str(customer.id),
        }

        expected_payload = {
            "id": str(account_id),
            "customer_id": str(customer.id),
            "account_type": "debit",
            "account_number": "12345",
            "account_balance": 10000,
            "created_at": "2018-11-13T15:16:08Z",
            "updated_at": "2018-11-13T15:16:08Z",
        }

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
            response = client.post("/dummy-bank/v1/accounts", json=payload)
            assert response.status_code == 201
            assert response.json() == expected_payload

    @pytest.mark.asyncio
    async def test_missing_customer(
        self,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
    ) -> None:
        payload = {
            "account_type": "debit",
            "account_number": "1234567890",
            "initial_balance": 100,
            "customer_id": "23fd1b92-4463-4659-913b-49ef7e4d48b9",
        }

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_account_repository() -> AccountsRepository:
            return account_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_account_repository] = (
            override_get_account_repository
        )

        with TestClient(app) as client:
            response = client.post("/dummy-bank/v1/accounts", json=payload)
            assert response.status_code == 404
            assert response.json() == {"detail": "customer not found"}

    @pytest.mark.parametrize(
        argnames=["field", "value"],
        argvalues=[
            ("account_type", None),
            ("account_type", "remove"),
            ("account_number", None),
            ("account_number", "remove"),
            ("initial_balance", None),
            ("initial_balance", "random_string"),
            ("initial_balance", "remove"),
            ("customer_id", "random_string"),
            ("customer_id", None),
            ("customer_id", "remove"),
        ],
    )
    @pytest.mark.asyncio
    async def test_bad_payload(
        self, customer_repository: CustomerRepository, field: str, value: Any
    ) -> None:
        payload = {
            "account_type": "debit",
            "account_number": "12345",
            "initial_balance": 100,
            "customer_id": "c57a1942-56ed-4e35-87af-2c4241b55149",
        }

        if value is not None and value == "remove":
            payload.pop(field)
        else:
            payload[field] = value

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )

        with TestClient(app) as client:
            response = client.post("/dummy-bank/v1/accounts", json=payload)
            assert response.status_code == 422
