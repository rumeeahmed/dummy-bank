from typing import Any, Callable
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_customer_repository
from api.main import create_app
from api.settings import Settings
from domain import Customer
from repository import CustomerRepository


class TestCustomerNotFound:
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository) -> None:
        payload = {"phone": "01234567890"}

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.patch(
                "/dummy-bank/v1/customers/cc5a6534-c35a-4f41-83bf-f0c69c6ad513",
                json=payload,
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "customer not found"}


@pytest.mark.parametrize(
    "field, original, updated",
    [
        ("first_name", "Rumee", "Bob"),
        ("middle_names", None, "Bobbington"),
        ("last_name", "Ahmed", "Bobberson"),
        ("phone", None, "01234567890"),
        ("email", "rumeeahmad@gmail.com", "bob.boberson@bob.com"),
    ],
)
class TestUpdateField:
    async def test(
        self,
        customer_repository: CustomerRepository,
        field: str,
        original: Any,
        updated: Any,
        make_customer: Callable[..., Customer],
    ) -> None:
        existing = make_customer(**{field: original})
        await customer_repository.save_customer(existing)

        assert getattr(existing, field) == original

        request = {field: updated}

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.patch(
                f"/dummy-bank/v1/customers/{existing.id}", json=request
            )
            assert response.status_code == 200
            assert response.json()[field] == updated
