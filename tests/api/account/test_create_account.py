from typing import Any, Callable
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from domain import Account, Customer
from repository import AccountsRepository, CustomerRepository


class TestCreateAccount:
    @patch("api.accounts.router.uuid4")
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test(
        self,
        mock_uuid: Mock,
        test_client: TestClient,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

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

        response = test_client.post("/dummy-bank/v1/accounts", json=payload)
        assert response.status_code == 201
        assert response.json() == expected_payload

    @pytest.mark.asyncio
    async def test_address_already_exists(
        self,
        test_client: TestClient,
        customer_repository: CustomerRepository,
        account_repository: AccountsRepository,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(
            customer_id=customer.id, account_type="debit", account_number="12345"
        )
        await account_repository.save_account(account)

        payload = {
            "account_type": "debit",
            "account_number": "12345",
            "initial_balance": 100,
            "customer_id": str(customer.id),
        }
        response = test_client.post("/dummy-bank/v1/accounts", json=payload)
        assert response.status_code == 409
        assert response.json() == {"detail": "account already exists"}

    @pytest.mark.asyncio
    async def test_missing_customer(self, test_client: TestClient) -> None:
        payload = {
            "account_type": "debit",
            "account_number": "1234567890",
            "initial_balance": 100,
            "customer_id": "23fd1b92-4463-4659-913b-49ef7e4d48b9",
        }
        response = test_client.post("/dummy-bank/v1/accounts", json=payload)
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
        self,
        test_client: TestClient,
        field: str,
        value: Any,
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

        response = test_client.post("/dummy-bank/v1/accounts", json=payload)
        assert response.status_code == 422
