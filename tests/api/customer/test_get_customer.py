from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from api.dependencies import get_customer_repository
from api.main import create_app
from api.settings import Settings
from domain import Customer
from repository import CustomerRepository


class TestGetCustomer:
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository) -> None:
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

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.get(f"/dummy-bank/v1/customers/{existing_customer.id}")
            assert response.status_code == 200
            assert response.json() == expected


class TestCustomerNotFound:
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository) -> None:
        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.get(f"/dummy-bank/v1/customers/{uuid4()}")
            assert response.status_code == 404
            assert response.json() == {"detail": "customer not found"}
