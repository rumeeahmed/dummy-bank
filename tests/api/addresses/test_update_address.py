from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from dummy_bank.lib.geolocation_client import Coordinates, GoogleMapsClient
from dummy_bank.repository import AddressesRepository, CustomerRepository

from ...make_domain_objects import MakeAddress, MakeCustomer


class TestAddressNotFound:
    @pytest.mark.asyncio
    async def test(
        self, addresses_repository: AddressesRepository, test_client: AsyncClient
    ) -> None:
        payload = {"building_name": "My building"}
        response = await test_client.patch(
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
        make_customer: MakeCustomer,
        addresses_repository: AddressesRepository,
        make_address: MakeAddress,
        field: str,
        original: str,
        updated: Any,
        test_client: AsyncClient,
    ) -> None:
        mock_get_coordinates.return_value = Coordinates(
            latitude="55.55", longitude="22.22"
        )
        customer = make_customer()
        await customer_repository.save_customer(customer)

        existing = make_address(**{field: original}, customer_id=customer.id)  # ty:ignore[invalid-argument-type]
        await addresses_repository.save_address(existing)
        assert getattr(existing, field) == original

        payload = {field: updated}

        response = await test_client.patch(
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
        make_customer: MakeCustomer,
        addresses_repository: AddressesRepository,
        make_address: MakeAddress,
        lat: str | None,
        lon: str | None,
        test_client: AsyncClient,
    ) -> None:
        mock_get_coordinates.side_effect = [Exception()]
        customer = make_customer()
        await customer_repository.save_customer(customer)

        existing = make_address(latitude=lat, longitude=lon, customer_id=customer.id)
        await addresses_repository.save_address(existing)

        payload = {"building_name": "My building"}

        response = await test_client.patch(
            f"/dummy-bank/v1/addresses/{existing.id}", json=payload
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["building_name"] == "My building"
        assert response_json["latitude"] == lat
        assert response_json["longitude"] == lon
