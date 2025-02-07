from typing import Any, Callable
from uuid import uuid4

import pytest

from domain import Account, Address, Customer


@pytest.fixture()
def make_customer(**kw: Any) -> Callable[..., Customer]:
    def _make_customer(**kw: Any) -> Customer:
        kwargs: dict = {
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


@pytest.fixture()
def make_account(**kw: Any) -> Callable[..., Account]:
    def _make_account(**kw: Any) -> Account:
        kwargs: dict = {
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


@pytest.fixture()
def make_address(**kw: Any) -> Callable[..., Address]:
    def _make_address(**kw: Any) -> Address:
        kwargs: dict = {
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
