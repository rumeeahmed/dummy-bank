from lib.authentication import QueryParamAuth
from lib.geolocation_client.geolocation_protocol import GeolocationProtocol
from lib.http_client.http_client import BaseHTTPClient

from .models import Coordinates


class GoogleMapsClient(BaseHTTPClient, GeolocationProtocol):
    def __init__(self, base_url: str, api_key: str) -> None:
        authorization = QueryParamAuth("key", api_key)
        super().__init__(base_url=base_url, authorization=authorization)

    async def get_coordinates(self, address: str) -> Coordinates | None:
        response = await self.get("/maps/api/geocode/json", params={"address": address})
        if response["results"] and response["status"] == "OK":
            return Coordinates(
                latitude=str(response["results"][0]["geometry"]["location"]["lat"]),
                longitude=str(response["results"][0]["geometry"]["location"]["lng"]),
            )
        return None
