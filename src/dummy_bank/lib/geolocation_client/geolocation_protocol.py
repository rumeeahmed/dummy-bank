from typing import Protocol

from .models import Coordinates


class GeolocationProtocol(Protocol):
    """
    Protocol for Geolocation clients.
    """

    async def get_coordinates(self, address: str) -> Coordinates | None:
        """
        Retrieve coordinates for given address.
        Args:
            address (str): Address to retrieve coordinates for.

        Returns (Coordinates | None): Coordinates for given address or None.
        """
        ...
