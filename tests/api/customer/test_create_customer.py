from typing import Any
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from api.dependencies import get_customer_repository
from api.main import create_app
from api.settings import Settings
from domain import Customer
from repository import CustomerRepository


class TestCustomerAlreadyExistsForUser:
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository) -> None:
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

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.post("/dummy-bank/v1/customers", json=payload)
            assert response.status_code == 409
            assert response.json() == {"detail": "customer already exists"}


class TestCreateCustomer:
    @patch("api.customers.router.uuid4")
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test(
        self,
        mock_uuid: Mock,
        customer_repository: CustomerRepository,
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

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.post("/dummy-bank/v1/customers", json=payload)
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
        self, customer_repository: CustomerRepository, field: str, value: Any
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

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.post("/dummy-bank/v1/customers", json=payload)
            assert response.status_code == 422
