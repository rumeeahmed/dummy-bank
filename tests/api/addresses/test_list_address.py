import asyncio
import uuid
from typing import Callable
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_address_repository, get_customer_repository
from api.main import create_app
from api.settings import Settings
from domain import Address, Customer
from repository import AddressesRepository, CustomerRepository


class TestListAddressesForNonExistingCustomer:
    @pytest.mark.asyncio
    async def test(
        self,
        customer_repository: CustomerRepository,
        addresses_repository: AddressesRepository,
    ) -> None:
        params = {"customer_id": "74505956-f7fe-4bf6-837a-aaa510b57b62"}

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_address_repository() -> AddressesRepository:
            return addresses_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )
        app.dependency_overrides[get_address_repository] = (
            override_get_address_repository
        )

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/addresses", params=params)
            assert response.status_code == 200
            assert response.json() == {
                "page": 1,
                "page_size": 50,
                "results": [],
                "total_count": 0,
                "total_pages": 0,
            }


class TestListAddressesThatDontExist:
    @pytest.mark.asyncio
    async def test(
        self,
        customer_repository: CustomerRepository,
        addresses_repository: AddressesRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)
        params = {"customer_id": str(customer.id)}

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_address_repository() -> AddressesRepository:
            return addresses_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )
        app.dependency_overrides[get_address_repository] = (
            override_get_address_repository
        )

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/accounts", params=params)
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
        addresses_repository: AddressesRepository,
        customer_repository: CustomerRepository,
        make_address: Callable[..., Address],
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
                addresses_repository.save_address(
                    make_address(
                        building_name=f"My House-{i}",
                        building_number=f"12345-{i}",
                        street=f"Some Street-{i}",
                        town=f"Some Town-{i}",
                        county=f"Some County-{i}",
                        post_code=f"Some Postcode-{i}",
                        country=f"Some Country-{i}",
                        customer_id=customer_id,
                    )
                )
            )

        await asyncio.gather(*coroutines)

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_address_repository() -> AddressesRepository:
            return addresses_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )
        app.dependency_overrides[get_address_repository] = (
            override_get_address_repository
        )

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/addresses", params=params)  # type: ignore
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
        addresses_repository: AddressesRepository,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        make_address: Callable[..., Address],
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
                addresses_repository.save_address(
                    make_address(
                        building_name=f"My House-{i}",
                        building_number=f"12345-{i}",
                        street=f"Some Street-{i}",
                        town=f"Some Town-{i}",
                        county=f"Some County-{i}",
                        post_code=f"Some Postcode-{i}",
                        country=f"Some Country-{i}",
                        customer_id=customer_id,
                    )
                )
            )

        await asyncio.gather(*coroutines)

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_address_repository() -> AddressesRepository:
            return addresses_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )
        app.dependency_overrides[get_address_repository] = (
            override_get_address_repository
        )

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/addresses", params=params)
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
    async def test_bad_params(
        self,
        customer_repository: CustomerRepository,
        addresses_repository: AddressesRepository,
        make_customer: Callable[..., Customer],
        params: dict,
    ) -> None:
        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_address_repository() -> AddressesRepository:
            return addresses_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )
        app.dependency_overrides[get_address_repository] = (
            override_get_address_repository
        )

        with TestClient(app) as client:
            response = client.get("/dummy-bank/v1/addresses", params=params)
            assert response.status_code == 422
