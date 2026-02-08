from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from freezegun import freeze_time

from httpx import AsyncClient
from dummy_bank.api.settings import Settings
from dummy_bank.domain import Customer
from dummy_bank.repository import CustomerRepository


class TestGetCustomer:
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository, test_client: AsyncClient) -> None:
        expected_id = UUID("9a4bdb0b-43cf-4efc-8a4c-260f8e117d9d")

        payload = {
            "email": "customer@example.com",
            "first_name": "John",
            "last_name": "Smith",
            "middle_names": "Smith",
            "phone": "+555555555",
        }

        existing_customer = Customer(
            **payload,
            id=expected_id,
            created_at=None,
            updated_at=None,
        )

        expected = {
            "id": str(expected_id),
            "created_at": "2018-11-13T15:16:08Z",
            "updated_at": "2018-11-13T15:16:08Z",
            "name": "John Smith Smith",
            **payload,
        }

        await customer_repository.save_customer(existing_customer)

        response = await test_client.get(f"/dummy-bank/v1/customers/{existing_customer.id}")
        assert response.status_code == 200
        assert response.json() == expected


class TestCustomerNotFound:
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository, test_client: AsyncClient) -> None:
        response = await test_client.get(f"/dummy-bank/v1/customers/{uuid4()}")
        assert response.status_code == 404
        assert response.json() == {"detail": "customer not found"}
