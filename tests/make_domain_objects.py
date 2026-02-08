from datetime import datetime
from typing import Final, Protocol, cast
from uuid import UUID, uuid4

import pytest

from dummy_bank.domain import Account, Address, Customer


class _UnsetType:
    pass


_UNSET: Final[_UnsetType] = _UnsetType()


class MakeCustomer(Protocol):
    def __call__(
        self,
        *,
        id: UUID | None | _UnsetType = _UNSET,
        created_at: datetime | None | _UnsetType = _UNSET,
        updated_at: datetime | None | _UnsetType = _UNSET,
        first_name: str | None | _UnsetType = _UNSET,
        middle_names: str | None | _UnsetType = _UNSET,
        last_name: str | None | _UnsetType = _UNSET,
        email: str | None | _UnsetType = _UNSET,
        phone: str | None | _UnsetType = _UNSET,
    ) -> Customer: ...


@pytest.fixture()
def make_customer() -> MakeCustomer:
    def _make_customer(
        *,
        id: UUID | None | _UnsetType = _UNSET,
        created_at: datetime | None | _UnsetType = _UNSET,
        updated_at: datetime | None | _UnsetType = _UNSET,
        first_name: str | None | _UnsetType = _UNSET,
        middle_names: str | None | _UnsetType = _UNSET,
        last_name: str | None | _UnsetType = _UNSET,
        email: str | None | _UnsetType = _UNSET,
        phone: str | None | _UnsetType = _UNSET,
    ) -> Customer:
        return Customer(
            id=cast(UUID, uuid4() if isinstance(id, _UnsetType) else id),
            created_at=cast(
                datetime | None,
                None if isinstance(created_at, _UnsetType) else created_at,
            ),
            updated_at=cast(
                datetime | None,
                None if isinstance(updated_at, _UnsetType) else updated_at,
            ),
            first_name=cast(
                str | None,
                "Bob" if isinstance(first_name, _UnsetType) else first_name,
            ),
            middle_names=cast(
                str | None,
                "Bobberson" if isinstance(middle_names, _UnsetType) else middle_names,
            ),
            last_name=cast(
                str | None,
                "Bobbington" if isinstance(last_name, _UnsetType) else last_name,
            ),
            email=cast(str | None, None if isinstance(email, _UnsetType) else email),
            phone=cast(str | None, None if isinstance(phone, _UnsetType) else phone),
        )

    return _make_customer


class MakeAccount(Protocol):
    def __call__(
        self,
        *,
        id: UUID | None | _UnsetType = _UNSET,
        created_at: datetime | None | _UnsetType = _UNSET,
        updated_at: datetime | None | _UnsetType = _UNSET,
        customer_id: UUID | None | _UnsetType = _UNSET,
        account_type: str | None | _UnsetType = _UNSET,
        account_number: str | None | _UnsetType = _UNSET,
        account_balance: int | float | None | _UnsetType = _UNSET,
        is_new: bool | None | _UnsetType = _UNSET,
    ) -> Account: ...


@pytest.fixture()
def make_account() -> MakeAccount:
    def _make_account(
        *,
        id: UUID | None | _UnsetType = _UNSET,
        created_at: datetime | None | _UnsetType = _UNSET,
        updated_at: datetime | None | _UnsetType = _UNSET,
        customer_id: UUID | None | _UnsetType = _UNSET,
        account_type: str | None | _UnsetType = _UNSET,
        account_number: str | None | _UnsetType = _UNSET,
        account_balance: int | float | None | _UnsetType = _UNSET,
        is_new: bool | None | _UnsetType = _UNSET,
    ) -> Account:
        return Account(
            id=cast(UUID, uuid4() if isinstance(id, _UnsetType) else id),
            created_at=cast(
                datetime | None,
                None if isinstance(created_at, _UnsetType) else created_at,
            ),
            updated_at=cast(
                datetime | None,
                None if isinstance(updated_at, _UnsetType) else updated_at,
            ),
            customer_id=cast(
                UUID,
                uuid4() if isinstance(customer_id, _UnsetType) else customer_id,
            ),
            account_type=cast(
                str,
                "Current" if isinstance(account_type, _UnsetType) else account_type,
            ),
            account_number=cast(
                str,
                "12345" if isinstance(account_number, _UnsetType) else account_number,
            ),
            account_balance=cast(
                int | float,
                0 if isinstance(account_balance, _UnsetType) else account_balance,
            ),
            is_new=cast(bool, True if isinstance(is_new, _UnsetType) else is_new),
        )

    return _make_account


class MakeAddress(Protocol):
    def __call__(
        self,
        *,
        id: UUID | None | _UnsetType = _UNSET,
        created_at: datetime | None | _UnsetType = _UNSET,
        updated_at: datetime | None | _UnsetType = _UNSET,
        customer_id: UUID | None | _UnsetType = _UNSET,
        building_name: str | None | _UnsetType = _UNSET,
        building_number: str | None | _UnsetType = _UNSET,
        street: str | None | _UnsetType = _UNSET,
        town: str | None | _UnsetType = _UNSET,
        post_code: str | None | _UnsetType = _UNSET,
        county: str | None | _UnsetType = _UNSET,
        country: str | None | _UnsetType = _UNSET,
        latitude: str | None | _UnsetType = _UNSET,
        longitude: str | None | _UnsetType = _UNSET,
    ) -> Address: ...


@pytest.fixture()
def make_address() -> MakeAddress:
    def _make_address(
        *,
        id: UUID | None | _UnsetType = _UNSET,
        created_at: datetime | None | _UnsetType = _UNSET,
        updated_at: datetime | None | _UnsetType = _UNSET,
        customer_id: UUID | None | _UnsetType = _UNSET,
        building_name: str | None | _UnsetType = _UNSET,
        building_number: str | None | _UnsetType = _UNSET,
        street: str | None | _UnsetType = _UNSET,
        town: str | None | _UnsetType = _UNSET,
        post_code: str | None | _UnsetType = _UNSET,
        county: str | None | _UnsetType = _UNSET,
        country: str | None | _UnsetType = _UNSET,
        latitude: str | None | _UnsetType = _UNSET,
        longitude: str | None | _UnsetType = _UNSET,
    ) -> Address:
        return Address(
            id=cast(UUID, uuid4() if isinstance(id, _UnsetType) else id),
            created_at=cast(
                datetime | None,
                None if isinstance(created_at, _UnsetType) else created_at,
            ),
            updated_at=cast(
                datetime | None,
                None if isinstance(updated_at, _UnsetType) else updated_at,
            ),
            customer_id=cast(
                UUID,
                uuid4() if isinstance(customer_id, _UnsetType) else customer_id,
            ),
            building_name=cast(
                str | None,
                "My Building"
                if isinstance(building_name, _UnsetType)
                else building_name,
            ),
            building_number=cast(
                str,
                "12345" if isinstance(building_number, _UnsetType) else building_number,
            ),
            street=cast(
                str,
                "Some street" if isinstance(street, _UnsetType) else street,
            ),
            town=cast(str, "Some town" if isinstance(town, _UnsetType) else town),
            post_code=cast(
                str,
                "Some postcode" if isinstance(post_code, _UnsetType) else post_code,
            ),
            county=cast(
                str | None,
                "Some county" if isinstance(county, _UnsetType) else county,
            ),
            country=cast(
                str,
                "Some country" if isinstance(country, _UnsetType) else country,
            ),
            latitude=cast(
                str | None,
                "123" if isinstance(latitude, _UnsetType) else latitude,
            ),
            longitude=cast(
                str | None,
                "123" if isinstance(longitude, _UnsetType) else longitude,
            ),
        )

    return _make_address
