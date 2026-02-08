from datetime import datetime
from typing import Final, Protocol
from uuid import UUID, uuid4

import pytest

from dummy_bank.domain import Account, Address, Customer

# ---------------------------------------------------------------------------
# Sentinel (distinguishes "not provided" from "provided as None")
# ---------------------------------------------------------------------------

_UNSET: Final = object()


class MakeCustomer(Protocol):
    def __call__(
        self,
        *,
        id: UUID | None | object = _UNSET,
        created_at: datetime | None | object = _UNSET,
        updated_at: datetime | None | object = _UNSET,
        first_name: str | None | object = _UNSET,
        middle_names: str | None | object = _UNSET,
        last_name: str | None | object = _UNSET,
        email: str | None | object = _UNSET,
        phone: str | None | object = _UNSET,
    ) -> Customer: ...


@pytest.fixture()
def make_customer() -> MakeCustomer:
    def _make_customer(
        *,
        id: UUID | None | object = _UNSET,
        created_at: datetime | None | object = _UNSET,
        updated_at: datetime | None | object = _UNSET,
        first_name: str | None | object = _UNSET,
        middle_names: str | None | object = _UNSET,
        last_name: str | None | object = _UNSET,
        email: str | None | object = _UNSET,
        phone: str | None | object = _UNSET,
    ) -> Customer:
        return Customer(
            id=uuid4() if id is _UNSET else id,
            created_at=None if created_at is _UNSET else created_at,
            updated_at=None if updated_at is _UNSET else updated_at,
            first_name="Bob" if first_name is _UNSET else first_name,
            middle_names="Bobberson" if middle_names is _UNSET else middle_names,
            last_name="Bobbington" if last_name is _UNSET else last_name,
            email=None if email is _UNSET else email,
            phone=None if phone is _UNSET else phone,
        )

    return _make_customer


class MakeAccount(Protocol):
    def __call__(
        self,
        *,
        id: UUID | None | object = _UNSET,
        created_at: datetime | None | object = _UNSET,
        updated_at: datetime | None | object = _UNSET,
        customer_id: UUID | None | object = _UNSET,
        account_type: str | None | object = _UNSET,
        account_number: str | None | object = _UNSET,
        account_balance: int | float | None | object = _UNSET,
        is_new: bool | object = _UNSET,
    ) -> Account: ...


@pytest.fixture()
def make_account() -> MakeAccount:
    def _make_account(
        *,
        id: UUID | None | object = _UNSET,
        created_at: datetime | None | object = _UNSET,
        updated_at: datetime | None | object = _UNSET,
        customer_id: UUID | None | object = _UNSET,
        account_type: str | None | object = _UNSET,
        account_number: str | None | object = _UNSET,
        account_balance: int | float | None | object = _UNSET,
        is_new: bool | object = _UNSET,
    ) -> Account:
        return Account(
            id=uuid4() if id is _UNSET else id,
            created_at=None if created_at is _UNSET else created_at,
            updated_at=None if updated_at is _UNSET else updated_at,
            customer_id=uuid4() if customer_id is _UNSET else customer_id,
            account_type="Current" if account_type is _UNSET else account_type,
            account_number="12345" if account_number is _UNSET else account_number,
            account_balance=0 if account_balance is _UNSET else account_balance,
            is_new=True if is_new is _UNSET else is_new,
        )

    return _make_account


class MakeAddress(Protocol):
    def __call__(
        self,
        *,
        id: UUID | None | object = _UNSET,
        created_at: datetime | None | object = _UNSET,
        updated_at: datetime | None | object = _UNSET,
        customer_id: UUID | None | object = _UNSET,
        building_name: str | None | object = _UNSET,
        building_number: str | None | object = _UNSET,
        street: str | None | object = _UNSET,
        town: str | None | object = _UNSET,
        post_code: str | None | object = _UNSET,
        county: str | None | object = _UNSET,
        country: str | None | object = _UNSET,
        latitude: str | None | object = _UNSET,
        longitude: str | None | object = _UNSET,
    ) -> Address: ...


@pytest.fixture()
def make_address() -> MakeAddress:
    def _make_address(
        *,
        id: UUID | None | object = _UNSET,
        created_at: datetime | None | object = _UNSET,
        updated_at: datetime | None | object = _UNSET,
        customer_id: UUID | None | object = _UNSET,
        building_name: str | None | object = _UNSET,
        building_number: str | None | object = _UNSET,
        street: str | None | object = _UNSET,
        town: str | None | object = _UNSET,
        post_code: str | None | object = _UNSET,
        county: str | None | object = _UNSET,
        country: str | None | object = _UNSET,
        latitude: str | None | object = _UNSET,
        longitude: str | None | object = _UNSET,
    ) -> Address:
        return Address(
            id=uuid4() if id is _UNSET else id,
            created_at=None if created_at is _UNSET else created_at,
            updated_at=None if updated_at is _UNSET else updated_at,
            customer_id=uuid4() if customer_id is _UNSET else customer_id,
            building_name="My Building" if building_name is _UNSET else building_name,
            building_number="12345" if building_number is _UNSET else building_number,
            street="Some street" if street is _UNSET else street,
            town="Some town" if town is _UNSET else town,
            post_code="Some postcode" if post_code is _UNSET else post_code,
            county="Some county" if county is _UNSET else county,
            country="Some country" if country is _UNSET else country,
            latitude="123" if latitude is _UNSET else latitude,
            longitude="123" if longitude is _UNSET else longitude,
        )

    return _make_address
