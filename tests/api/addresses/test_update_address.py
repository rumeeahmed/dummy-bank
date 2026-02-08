from typing import Any, Callable
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from dummy_bank.api.dependencies import (
    get_address_repository,
    get_customer_repository,
)
from dummy_bank.api.main import create_app
from dummy_bank.api.settings import Settings
from dummy_bank.domain import Address, Customer
from dummy_bank.lib.geolocation_client import Coordinates, GoogleMapsClient
from dummy_bank.repository import AddressesRepository, CustomerRepository


class TestAddressNotFound:
    @pytest.mark.asyncio
    async def test(self, addresses_repository: AddressesRepository) -> None:
        payload = {"building_name": "My building"}

        def override_get_address_repository() -> AddressesRepository:
            return addresses_repository

        app = create_app(settings=Settings(), logger=Mock())
        app.dependency_overrides[get_address_repository] = (
            override_get_address_repository
        )

        with TestClient(app) as client:
            response = client.patch(
                "/dummy-bank/v1/addresses/cc5a6534-c35a-4f41-83bf-f0c69c6ad513",
                json=payload,
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "address not found"}


class TestUpdateField:
    @pytest.mark.parametrize(
        "field, original, updated",
        [
            ("building_name", "Cool Building", "My Building"),
            ("building_name", "Cool Building", None),
            ("building_number", "146", "56"),
            ("street", "Cool Street", "Not so cool street"),
            ("town", "Luton", "London"),
            ("post_code", "LU2 123", "E14 123"),
            ("county", "Bedfordshire", "Warwickshire"),
            ("county", "Bedfordshire", None),
            ("country", "England", "United Kingdom"),
        ],
    )
    @pytest.mark.asyncio
    @patch.object(GoogleMapsClient, "get_coordinates")
    async def test(
        self,
        mock_get_coordinates: MagicMock,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        addresses_repository: AddressesRepository,
        make_address: Callable[..., Address],
        field: str,
        original: str,
        updated: Any,
    ) -> None:
        mock_get_coordinates.return_value = Coordinates(
            latitude="55.55", longitude="22.22"
        )
        customer = make_customer()
        await customer_repository.save_customer(customer)

        existing = make_address(**{field: original}, customer_id=customer.id)
        await addresses_repository.save_address(existing)

        assert getattr(existing, field) == original

        payload = {field: updated}

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
            response = client.patch(
                f"/dummy-bank/v1/addresses/{existing.id}", json=payload
            )
            assert response.status_code == 200
            response_json = response.json()
            assert response_json[field] == updated
            assert response_json["latitude"] == "55.55"
            assert response_json["longitude"] == "22.22"

    @pytest.mark.parametrize(
        "lat, lon",
        [
            (None, None),
            ("444", "666"),
        ],
    )
    @pytest.mark.asyncio
    @patch.object(GoogleMapsClient, "get_coordinates")
    async def test_original_lat_lon_null_update_raises_exception(
        self,
        mock_get_coordinates: MagicMock,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        addresses_repository: AddressesRepository,
        make_address: Callable[..., Address],
        lat: str | None,
        lon: str | None,
    ) -> None:
        mock_get_coordinates.side_effect = [Exception()]
        customer = make_customer()
        await customer_repository.save_customer(customer)

        existing = make_address(latitude=lat, longitude=lon, customer_id=customer.id)
        await addresses_repository.save_address(existing)

        payload = {"building_name": "My building"}

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
            response = client.patch(
                f"/dummy-bank/v1/addresses/{existing.id}", json=payload
            )
            assert response.status_code == 200
            response_json = response.json()
            assert response_json["building_name"] == "My building"
            assert response_json["latitude"] == lat
            assert response_json["longitude"] == lon
