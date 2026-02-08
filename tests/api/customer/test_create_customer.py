from httpx import AsyncClient
from typing import Any
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from freezegun import freeze_time

from dummy_bank.api.settings import Settings
from dummy_bank.domain import Customer
from dummy_bank.repository import CustomerRepository


class TestCustomerAlreadyExists:
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository, test_client: AsyncClient) -> None:
        payload = {
            "email": "customer@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "middle_names": "Smith",
            "phone": "+555555555",
        }

        existing_customer = Customer(
            **payload,
            id=UUID("cc5a6534-c35a-4f41-83bf-f0c69c6ad513"),
            created_at=None,
            updated_at=None,
        )

        await customer_repository.save_customer(existing_customer)

        response = await test_client.post("/dummy-bank/v1/customers", json=payload)
        assert response.status_code == 409
        assert response.json() == {"detail": "customer already exists"}


class TestCreateCustomer:
    @patch("dummy_bank.api.customers.router.uuid4")
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test(
        self,
        mock_uuid: Mock,
        customer_repository: CustomerRepository, test_client: AsyncClient
    ) -> None:
        expected_id = UUID("9a4bdb0b-43cf-4efc-8a4c-260f8e117d9d")
        mock_uuid.return_value = expected_id

        payload = {
            "email": "john.smith@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "middle_names": "Smith",
            "phone": "+555555555",
        }

        expected = {
            "id": str(expected_id),
            "created_at": "2018-11-13T15:16:08Z",
            "updated_at": "2018-11-13T15:16:08Z",
            "name": "John Smith Smith",
            **payload,
        }

        response = await test_client.post("/dummy-bank/v1/customers", json=payload)
        assert response.status_code == 201
        assert response.json() == expected

    @pytest.mark.parametrize(
        argnames=["field", "value"],
        argvalues=[
            ("email", "dummy"),
            ("first_name", None),
            ("first_name", "remove"),
            ("last_name", None),
            ("last_name", "remove"),
        ],
    )
    @pytest.mark.asyncio
    async def test_bad_payload(
        self, customer_repository: CustomerRepository, field: str, value: Any , test_client: AsyncClient
    ) -> None:
        payload = {
            "email": "john.smith@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "middle_names": "Smith",
            "phone": "+555555555",
        }

        if value is not None and value == "remove":
            payload.pop(field)
        else:
            payload[field] = value

        response = await test_client.post("/dummy-bank/v1/customers", json=payload)
        assert response.status_code == 422
