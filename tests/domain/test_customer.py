from datetime import datetime, timezone
from typing import Callable
from uuid import UUID

import pytest

from domain import Customer


class TestID:
    def test_init_valid(self, make_customer: Callable[..., Customer]) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        customer = make_customer(id=value)
        assert customer.id == value

    def test_is_read_only(self, make_customer: Callable[..., Customer]) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        customer = make_customer(id=value)

        with pytest.raises(AttributeError):
            customer.id = UUID("c668e0af-d1b9-412f-a1da-790e5905da26")  # type: ignore[misc]


class TestCreatedAt:
    VALID_VALUES = [None, datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: datetime | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(created_at=value)
        assert customer.created_at == value

    def test_is_settable_if_none(self, make_customer: Callable[..., Customer]) -> None:
        customer = make_customer(created_at=None)
        customer.created_at = datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)
        assert customer.created_at == datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)

    def test_is_read_only_if_not_none(
        self, make_customer: Callable[..., Customer]
    ) -> None:
        value = datetime(2024, 6, 26, 1, 2, 3, 4, tzinfo=timezone.utc)
        customer = make_customer(created_at=value)

        with pytest.raises(AttributeError):
            customer.created_at = datetime.now(timezone.utc)

        assert customer.created_at == value


class TestUpdatedAt:
    VALID_VALUES = [None, datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: datetime | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(updated_at=value)
        assert customer.updated_at == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: datetime | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(updated_at=None)
        customer.updated_at = value
        assert customer.updated_at == value


class TestPhone:
    VALID_VALUES = [None, "01234567890"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(phone=value)
        assert customer.phone == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer()
        customer.phone = value
        assert customer.phone == value


class TestFirstName:
    VALID_VALUES = [None, "Rumee"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(first_name=value)
        assert customer.first_name == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(first_name=None)
        customer.first_name = value
        assert customer.first_name == value


class TestMiddleNames:
    VALID_VALUES = [None, "Bob Bobbington"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(middle_names=value)
        assert customer.middle_names == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(middle_names=None)
        customer.middle_names = value
        assert customer.middle_names == value


class TestLastName:
    VALID_VALUES = [None, "01234567890"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(last_name=value)
        assert customer.last_name == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer()
        customer.last_name = value
        assert customer.last_name == value


class TestName:
    @pytest.mark.parametrize(
        ["first_name", "middle_names", "last_name", "expected"],
        [
            ("Rumee", "Bob Bobbington", "Ahmed", "Rumee Bob Bobbington Ahmed"),
            ("Rumee", None, "Ahmed", "Rumee Ahmed"),
            (None, None, None, None),
            (None, "Bob Bobbington", None, None),
        ],
        ids=[
            "all names present",
            "middle names not present",
            "no names present",
            "first name last name missing",
        ],
    )
    def test(
        self,
        first_name: str | None,
        middle_names: str | None,
        last_name: str | None,
        expected: str | None,
        make_customer: Callable[..., Customer],
    ) -> None:
        customer = make_customer(
            first_name=first_name, middle_names=middle_names, last_name=last_name
        )
        assert customer.name == expected


class TestEmail:
    VALID_VALUES = [None, "bob@example.com"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer(email=value)
        assert customer.email == value

    def test_init_invalid(self, make_customer: Callable[..., Customer]) -> None:
        with pytest.raises(ValueError):
            make_customer(email="bob")

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_customer: Callable[..., Customer]
    ) -> None:
        customer = make_customer()
        customer.email = value
        assert customer.email == value

    def test_set_invalid(self, make_customer: Callable[..., Customer]) -> None:
        customer = make_customer()
        with pytest.raises(ValueError):
            customer.email = "bob"
