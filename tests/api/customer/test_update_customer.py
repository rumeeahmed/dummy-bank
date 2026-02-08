from alembic.op import f
from typing import Any
from unittest.mock import Mock
from httpx import AsyncClient
import pytest

from dummy_bank.api.settings import Settings
from dummy_bank.repository import CustomerRepository

from ...make_domain_objects import MakeCustomer


class TestCustomerNotFound:
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository, test_client: AsyncClient) -> None:
        payload = {"phone": "01234567890"}
        response = await test_client.patch(
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
        make_customer: MakeCustomer,
            test_client: AsyncClient,
    ) -> None:
        existing = make_customer(**{field: original})
        await customer_repository.save_customer(existing)
        assert getattr(existing, field) == original

        request = {field: updated}
        response = await test_client.patch(
            f"/dummy-bank/v1/customers/{existing.id}", json=request
        )
        assert response.status_code == 200
        assert response.json()[field] == updated
