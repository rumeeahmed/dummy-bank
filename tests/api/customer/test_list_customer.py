import asyncio
from typing import Callable
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from dummy_bank.api.dependencies import get_customer_repository
from dummy_bank.api.main import create_app
from dummy_bank.api.settings import Settings
from dummy_bank.domain import Customer
from dummy_bank.repository import CustomerRepository


class TestListCustomersThatDontExist:
    @pytest.mark.asyncio
    async def test(self, customer_repository: CustomerRepository) -> None:
        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/customers")
            assert response.status_code == 200
            assert response.json() == {
                "page": 1,
                "page_size": 50,
                "results": [],
                "total_count": 0,
                "total_pages": 0,
            }


class TestListCustomers:
    @pytest.mark.parametrize(
        argnames=["page", "page_size", "expected_total_pages"],
        argvalues=[
            (1, 5, 4),
            (1, 4, 5),
        ],
    )
    @pytest.mark.asyncio
    async def test(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        page: int,
        page_size: int,
        expected_total_pages: int,
    ) -> None:
        params = {"page": page, "page_size": page_size}
        coroutines = []
        for i in range(20):
            coroutines.append(
                customer_repository.save_customer(
                    make_customer(
                        email=f"john.smith_{i}@example.com",
                        first_name=f"John_{i}",
                        last_name=f"Smith_{i}",
                        middle_names=f"Smith_{i}",
                        phone=f"+555555555_{i}",
                    )
                )
            )

        await asyncio.gather(*coroutines)

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/customers", params=params)
            assert response.status_code == 200

            response_json = response.json()
            assert len(response_json["results"]) == page_size
            assert response_json["total_count"] == 20
            assert response_json["total_pages"] == expected_total_pages
            assert response_json["page"] == page
            assert response_json["page_size"] == page_size

    @pytest.mark.asyncio
    async def test_default_page_params(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        coroutines = []
        for i in range(20):
            coroutines.append(
                customer_repository.save_customer(
                    make_customer(
                        email=f"john.smith_{i}@example.com",
                        first_name=f"John_{i}",
                        last_name=f"Smith_{i}",
                        middle_names=f"Smith_{i}",
                        phone=f"+555555555_{i}",
                    )
                )
            )

        await asyncio.gather(*coroutines)

        def override_get_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = override_get_repository

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/customers")
            assert response.status_code == 200

            response_json = response.json()
            assert len(response_json["results"]) == 20
            assert response_json["total_count"] == 20
            assert response_json["total_pages"] == 1
            assert response_json["page"] == 1
            assert response_json["page_size"] == 50
