from datetime import datetime
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
        post_code: str,
        county: str | None,
        country: str,
    ) -> None:
        self._id = id
        self._customer_id = customer_id
        self._created_at = created_at
        self.updated_at = updated_at
        self.building_name = building_name
        self.building_number = building_number
        self.street = street
        self.post_code = post_code
        self.county = county
        self.country = country

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
