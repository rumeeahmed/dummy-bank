import uuid
from typing import Any, Callable
from unittest.mock import MagicMock, Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from dummy_bank.api.dependencies import (
    get_address_repository,
    get_customer_repository,
)
from dummy_bank.api.main import create_app
from dummy_bank.api.settings import Settings
from dummy_bank.domain import Address, Customer
from dummy_bank.lib.geolocation_client import Coordinates, GoogleMapsClient
from dummy_bank.repository import AddressesRepository, CustomerRepository


class TestCreateAddress:
    @patch.object(GoogleMapsClient, "get_coordinates")
    @patch("api.adresses.router.uuid4")
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test(
        self,
        mock_uuid: Mock,
        mock_get_coordinates: MagicMock,
        customer_repository: CustomerRepository,
        addresses_repository: AddressesRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        mock_get_coordinates.return_value = Coordinates(
            latitude="55.55", longitude="22.22"
        )

        customer = make_customer()
        await customer_repository.save_customer(customer)

        loaded_customer = await customer_repository.load_customer_with_id(customer.id)
        assert loaded_customer is not None

        address_id = UUID("c57a1942-56ed-4e35-87af-2c4241b55149")
        mock_uuid.return_value = address_id

        payload = {
            "building_name": "Default Building",
            "building_number": "123",
            "street": "Main Street",
            "town": "Springfield",
            "post_code": "AB12 3CD",
            "county": "Default County",
            "country": "Default Country",
            "customer_id": str(customer.id),
        }

        expected_payload = {
            **payload,
            "id": str(address_id),
            "customer_id": str(customer.id),
            "latitude": "55.55",
            "longitude": "22.22",
            "created_at": "2018-11-13T15:16:08Z",
            "updated_at": "2018-11-13T15:16:08Z",
            "display_address": "Default Building, 123, Main Street, Springfield, Default County, AB12 3CD, Default Country",
        }

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
            response = client.post("/dummy-bank/v1/addresses", json=payload)
            assert response.status_code == 201
            assert response.json() == expected_payload

    @pytest.mark.asyncio
    async def test_customer_address_exists(
        self,
        customer_repository: CustomerRepository,
        addresses_repository: AddressesRepository,
        make_customer: Callable[..., Customer],
        make_address: Callable[..., Address],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        address = make_address(
            post_code="Some postcode", customer_id=customer.id, id=uuid.uuid4()
        )

        await addresses_repository.save_address(address)

        payload = {
            "building_name": "Default Building",
            "building_number": "123",
            "street": "Main Street",
            "town": "Springfield",
            "post_code": "Some postcode",
            "county": "Default County",
            "country": "Default Country",
            "customer_id": str(customer.id),
        }

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
            response = client.post("/dummy-bank/v1/addresses", json=payload)
            assert response.status_code == 409
            assert response.json() == {"detail": "address already exists"}

    @patch.object(GoogleMapsClient, "get_coordinates")
    @patch("api.adresses.router.uuid4")
    @freeze_time("2018-11-13T15:16:08")
    @pytest.mark.asyncio
    async def test_bad_geolocation_request(
        self,
        mock_uuid: Mock,
        mock_get_coordinates: MagicMock,
        customer_repository: CustomerRepository,
        addresses_repository: AddressesRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        mock_get_coordinates.side_effect = [Exception()]

        customer = make_customer()
        await customer_repository.save_customer(customer)

        loaded_customer = await customer_repository.load_customer_with_id(customer.id)
        assert loaded_customer is not None

        address_id = UUID("c57a1942-56ed-4e35-87af-2c4241b55149")
        mock_uuid.return_value = address_id

        payload = {
            "building_name": "Default Building",
            "building_number": "123",
            "street": "Main Street",
            "town": "Springfield",
            "post_code": "AB12 3CD",
            "county": "Default County",
            "country": "Default Country",
            "customer_id": str(customer.id),
        }

        expected_payload = {
            **payload,
            "id": str(address_id),
            "customer_id": str(customer.id),
            "latitude": None,
            "longitude": None,
            "created_at": "2018-11-13T15:16:08Z",
            "updated_at": "2018-11-13T15:16:08Z",
            "display_address": "Default Building, 123, Main Street, Springfield, Default County, AB12 3CD, Default Country",
        }

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
            response = client.post("/dummy-bank/v1/addresses", json=payload)
            assert response.status_code == 201
            assert response.json() == expected_payload

    @pytest.mark.asyncio
    async def test_missing_customer(
        self,
        customer_repository: CustomerRepository,
        addresses_repository: AddressesRepository,
    ) -> None:
        payload = {
            "building_name": "Default Building",
            "building_number": "123",
            "street": "Main Street",
            "town": "Springfield",
            "post_code": "AB12 3CD",
            "county": "Default County",
            "country": "Default Country",
            "customer_id": "6199687f-3c89-4c92-a532-28ec5f1d5f32",
        }

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        def override_get_address_repository() -> AddressesRepository:
            return addresses_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_address_repository] = (
            override_get_address_repository
        )
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )

        with TestClient(app) as client:
            response = client.post("/dummy-bank/v1/addresses", json=payload)
            assert response.status_code == 404
            assert response.json() == {"detail": "customer not found"}

    @pytest.mark.parametrize(
        argnames=["field", "value"],
        argvalues=[
            ("building_number", None),
            ("building_number", "remove"),
            ("street", None),
            ("street", "remove"),
            ("town", None),
            ("town", "remove"),
            ("post_code", None),
            ("post_code", "remove"),
            ("country", None),
            ("country", "remove"),
            ("customer_id", "random_string"),
            ("customer_id", None),
            ("customer_id", "remove"),
        ],
    )
    @pytest.mark.asyncio
    async def test_bad_payload(
        self, customer_repository: CustomerRepository, field: str, value: Any
    ) -> None:
        payload = {
            "building_name": "Default Building",
            "building_number": "123",
            "street": "Main Street",
            "town": "Springfield",
            "post_code": "AB12 3CD",
            "county": "Default County",
            "country": "Default Country",
            "customer_id": "6199687f-3c89-4c92-a532-28ec5f1d5f32",
        }

        if value is not None and value == "remove":
            payload.pop(field)
        else:
            payload[field] = value

        def override_get_customer_repository() -> CustomerRepository:
            return customer_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_customer_repository] = (
            override_get_customer_repository
        )

        with TestClient(app) as client:
            response = client.post("/dummy-bank/v1/addresses", json=payload)
            assert response.status_code == 422
