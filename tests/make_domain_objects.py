from typing import Any, Protocol, TypedDict
from uuid import UUID, uuid4

import pytest

from dummy_bank.domain import Account, Address, Customer


class CustomerKwargs(TypedDict, total=False):
    id: UUID
    created_at: None
    updated_at: None
    first_name: str
    middle_names: str
    last_name: str
    email: str | None
    phone: str | None


class MakeCustomer(Protocol):
    def __call__(self, **overrides: CustomerKwargs) -> Customer: ...


@pytest.fixture()
def make_customer() -> MakeCustomer:
    def _make_customer(**kw: Any) -> Customer:
        kwargs: CustomerKwargs = {
            "id": uuid4(),
            "created_at": None,
            "updated_at": None,
            "first_name": "Bob",
            "middle_names": "Bobberson",
            "last_name": "Bobbington",
            "email": None,
            "phone": None,
        }
        return Customer(**{**kwargs, **kw})

    return _make_customer


class MakeAccount(Protocol):
    def __call__(self, **overrides: CustomerKwargs) -> Account: ...


class AccountKwargs(TypedDict, total=False):
    id: UUID
    created_at: None
    updated_at: None
    customer_id: UUID
    account_type: str
    account_number: str
    account_balance: int


@pytest.fixture()
def make_account() -> MakeAccount:
    def _make_account(**kw: Any) -> Account:
        kwargs: AccountKwargs = {
            "id": uuid4(),
            "customer_id": uuid4(),
            "created_at": None,
            "updated_at": None,
            "account_type": "Current",
            "account_number": "12345",
            "account_balance": 0,
        }
        return Account(**{**kwargs, **kw})

    return _make_account


class MakeAddress(Protocol):
    def __call__(self, **overrides: CustomerKwargs) -> Address: ...


class AddressKwargs(TypedDict, total=False):
    id: UUID
    created_at: None
    updated_at: None
    customer_id: UUID
    building_name: str
    building_number: str
    street: str
    town: str
    post_code: str
    county: str
    street: str
    country: str
    latitude: str
    longitude: str


@pytest.fixture()
def make_address() -> MakeAddress:
    def _make_address(**kw: Any) -> Address:
        kwargs: AddressKwargs = {
            "id": uuid4(),
            "customer_id": uuid4(),
            "created_at": None,
            "updated_at": None,
            "building_name": "My Building",
            "building_number": "12345",
            "street": "Some street",
            "town": "Some town",
            "post_code": "Some postcode",
            "county": "Some county",
            "country": "Some country",
            "latitude": "123",
            "longitude": "123",
        }
        return Address(**{**kwargs, **kw})

    return _make_address
