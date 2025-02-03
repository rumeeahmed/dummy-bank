from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, validate_call


class Customer:
    @validate_call
    def __init__(
        self,
        *,
        id: UUID,
        created_at: datetime | None,
        updated_at: datetime | None,
        first_name: str | None,
        middle_names: str | None,
        last_name: str | None,
        email: EmailStr | None,
        phone: str | None,
    ) -> None:
        self._id = id
        self._created_at = created_at
        self.updated_at = updated_at
        self.first_name = first_name
        self.middle_names = middle_names
        self.last_name = last_name
        self._email = email
        self.phone = phone

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime | None) -> None:
        if self._created_at is not None:
            raise AttributeError("created_at cannot be set if not None")

        self._created_at = value

    @property
    def email(self) -> EmailStr | None:
        return self._email

    @email.setter
    @validate_call
    def email(self, value: EmailStr | None) -> None:
        self._email = value

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str | None:
        if not self.first_name and not self.last_name:
            return None

        name_parts = filter(None, [self.first_name, self.middle_names, self.last_name])
        full_name = " ".join(name_parts)

        return full_name if full_name else None
