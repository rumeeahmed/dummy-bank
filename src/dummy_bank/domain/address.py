from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import validate_call


class Address:
    @validate_call
    def __init__(
        self,
        *,
        id: UUID,
        customer_id: UUID,
        created_at: datetime | None,
        updated_at: datetime | None,
        building_name: str | None,
        building_number: str,
        street: str,
        town: str,
        post_code: str,
        county: str | None,
        country: str,
        latitude: str | None,
        longitude: str | None,
    ) -> None:
        self._id = id
        self._customer_id = customer_id
        self._created_at = created_at
        self.updated_at = updated_at
        self.building_name = building_name
        self.building_number = building_number
        self.street = street
        self.town = town
        self.post_code = post_code
        self.county = county
        self.country = country
        self.latitude = latitude
        self.longitude = longitude

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime | None) -> None:
        if self._created_at is not None:
            raise AttributeError("created_at cannot be set if not None")

        self._created_at = value

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def customer_id(self) -> UUID:
        return self._customer_id

    @property
    def display_address(self) -> str:
        components = [
            self.building_name,
            self.building_number,
            self.street,
            self.town,
            self.county,
            self.post_code,
            self.country,
        ]
        return ", ".join(filter(None, components))

    @classmethod
    def from_record(cls, record: Any) -> Self:
        return cls(
            id=record.id,
            customer_id=record.customer_id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            building_name=record.building_name,
            building_number=record.building_number,
            street=record.street,
            post_code=record.post_code,
            town=record.town,
            county=record.county,
            country=record.country,
            latitude=record.latitude,
            longitude=record.longitude,
        )
