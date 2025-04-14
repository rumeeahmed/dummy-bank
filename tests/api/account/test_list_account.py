import asyncio
import uuid
from typing import Callable

import pytest
from fastapi.testclient import TestClient

from domain import Account, Customer
from repository import AccountsRepository, CustomerRepository


class TestListAccountForNonExistingCustomer:
    @pytest.mark.asyncio
    async def test(self, test_client: TestClient) -> None:
        params = {"customer_id": "74505956-f7fe-4bf6-837a-aaa510b57b62"}
        response = test_client.get("/dummy-bank/v1/accounts", params=params)
        assert response.status_code == 200
        assert response.json() == {
            "page": 1,
            "page_size": 50,
            "results": [],
            "total_count": 0,
            "total_pages": 0,
        }


class TestListAccountsThatDontExist:
    @pytest.mark.asyncio
    async def test(
        self,
        test_client: TestClient,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)
        params = {"customer_id": str(customer.id)}

        response = test_client.get("/dummy-bank/v1/accounts", params=params)
        assert response.status_code == 200
        assert response.json() == {
            "page": 1,
            "page_size": 50,
            "results": [],
            "total_count": 0,
            "total_pages": 0,
        }


class TestListAccounts:
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
        test_client: TestClient,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: Callable[..., Account],
        make_customer: Callable[..., Customer],
        page: int,
        page_size: int,
        expected_total_pages: int,
    ) -> None:
        customer_id = uuid.uuid4()
        params = {"page": page, "page_size": page_size, "customer_id": str(customer_id)}

        await customer_repository.save_customer(
            make_customer(
                id=customer_id,
                email="john.smith@example.com",
                first_name="John",
                last_name="Smith",
                middle_names="Smith",
                phone="+555555555",
            )
        )
        await customer_repository.save_customer(
            make_customer(
                email="john.smith2@example.com",
                first_name="John2",
                last_name="Smith2",
                middle_names="Smith2",
                phone="+555555555",
            )
        )

        coroutines = []
        for i in range(20):
            coroutines.append(
                account_repository.save_account(
                    make_account(
                        account_type=f"john.smith_{i}",
                        account_number=f"John_{i}",
                        customer_id=customer_id,
                    )
                )
            )

        await asyncio.gather(*coroutines)

        response = test_client.get("/dummy-bank/v1/accounts", params=params)  # type: ignore
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
        test_client: TestClient,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        make_account: Callable[..., Account],
    ) -> None:
        customer_id = uuid.uuid4()
        params = {"customer_id": str(customer_id)}
        await customer_repository.save_customer(
            make_customer(
                id=customer_id,
                email="john.smith@example.com",
                first_name="John",
                last_name="Smith",
                middle_names="Smith",
                phone="+555555555",
            )
        )
        await customer_repository.save_customer(
            make_customer(
                email="john.smith2@example.com",
                first_name="John2",
                last_name="Smith2",
                middle_names="Smith2",
                phone="+555555555",
            )
        )
        coroutines = []
        for i in range(20):
            coroutines.append(
                account_repository.save_account(
                    make_account(
                        account_type=f"john.smith_{i}",
                        account_number=f"John_{i}",
                        customer_id=customer_id,
                    )
                )
            )

        await asyncio.gather(*coroutines)

        response = test_client.get("/dummy-bank/v1/accounts", params=params)
        assert response.status_code == 200

        response_json = response.json()
        assert len(response_json["results"]) == 20
        assert response_json["total_count"] == 20
        assert response_json["total_pages"] == 1
        assert response_json["page"] == 1
        assert response_json["page_size"] == 50

    @pytest.mark.parametrize(
        argnames="params", argvalues=[{}, {"customer_id": "dummy"}]
    )
    @pytest.mark.asyncio
    async def test_bad_params(self, test_client: TestClient, params: dict) -> None:
        response = test_client.get("/dummy-bank/v1/accounts", params=params)
        assert response.status_code == 422
