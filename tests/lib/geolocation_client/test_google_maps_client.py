import pytest
from pytest_httpx import HTTPXMock

from lib.geolocation_client import GoogleMapsClient
from lib.geolocation_client.models import Coordinates


class TestGoogleMapsClient:
    @pytest.mark.asyncio
    async def test(
        self,
        httpx_mock: HTTPXMock,
        google_maps_client: GoogleMapsClient,
        google_maps_url: str,
        google_maps_response: dict,
        google_maps_api_key: str,
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            url=f"{google_maps_url}/maps/api/geocode/json?address=Cool+road%2C+cool+town%2C+cool+postcode&key={google_maps_api_key}",
            json=google_maps_response,
        )

        expected_coordinates = Coordinates(
            latitude=str(
                google_maps_response["results"][0]["geometry"]["location"]["lat"]
            ),
            longitude=str(
                google_maps_response["results"][0]["geometry"]["location"]["lng"]
            ),
        )
        coordinates = await google_maps_client.get_coordinates(
            "Cool road, cool town, cool postcode"
        )
        assert coordinates is not None
        assert coordinates.model_dump() == expected_coordinates.model_dump()

    @pytest.mark.asyncio
    async def test_status_is_not_ok(
        self,
        httpx_mock: HTTPXMock,
        google_maps_client: GoogleMapsClient,
        google_maps_url: str,
        google_maps_response: dict,
        google_maps_api_key: str,
    ) -> None:
        response = {**google_maps_response, "status": "not ok"}
        httpx_mock.add_response(
            method="GET",
            url=f"{google_maps_url}/maps/api/geocode/json?address=Cool+road%2C+cool+town%2C+cool+postcode&key={google_maps_api_key}",
            json=response,
        )

        coordinates = await google_maps_client.get_coordinates(
            "Cool road, cool town, cool postcode"
        )
        assert coordinates is None
