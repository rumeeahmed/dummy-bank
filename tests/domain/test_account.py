import uuid
from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from dummy_bank.repository import DBAccount

from ..make_domain_objects import MakeAccount


class TestID:
    def test_init_valid(self, make_account: MakeAccount) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        account = make_account(id=value)
        assert account.id == value

    def test_is_read_only(self, make_account: MakeAccount) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        account = make_account(id=value)

        with pytest.raises(AttributeError):
            setattr(account, "id", UUID("c668e0af-d1b9-412f-a1da-790e5905da26"))


class TestCustomerID:
    def test_init_valid(self, make_account: MakeAccount) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        account = make_account(customer_id=value)
        assert account.customer_id == value

    def test_is_read_only(self, make_account: MakeAccount) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        account = make_account(customer_id=value)

        with pytest.raises(AttributeError):
            setattr(
                account, "customer_id", UUID("c668e0af-d1b9-412f-a1da-790e5905da26")
            )


class TestCreatedAt:
    VALID_VALUES = [None, datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: datetime | None, make_account: MakeAccount
    ) -> None:
        customer = make_account(created_at=value)
        assert customer.created_at == value

    def test_is_settable_if_none(self, make_account: MakeAccount) -> None:
        customer = make_account(created_at=None)
        customer.created_at = datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)
        assert customer.created_at == datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)

    def test_is_read_only_if_not_none(self, make_account: MakeAccount) -> None:
        value = datetime(2024, 6, 26, 1, 2, 3, 4, tzinfo=timezone.utc)
        customer = make_account(created_at=value)

        with pytest.raises(AttributeError):
            customer.created_at = datetime.now(timezone.utc)

        assert customer.created_at == value


class TestUpdatedAt:
    VALID_VALUES = [None, datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: datetime | None, make_account: MakeAccount
    ) -> None:
        customer = make_account(updated_at=value)
        assert customer.updated_at == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(self, value: datetime | None, make_account: MakeAccount) -> None:
        customer = make_account(updated_at=None)
        customer.updated_at = value
        assert customer.updated_at == value


class TestAccountNumber:
    def test_init_valid(self, make_account: MakeAccount) -> None:
        value = "1234567890"
        account = make_account(account_number=value)
        assert account.account_number == value

    def test_is_read_only(self, make_account: MakeAccount) -> None:
        value = "1234567890"
        account = make_account(account_number=value)

        with pytest.raises(AttributeError):
            setattr(account, "account_number", "12334")


class TestAccountType:
    def test_init_valid(self, make_account: MakeAccount) -> None:
        value = "credit"
        account = make_account(account_type=value)
        assert account.account_type == value

    def test_is_read_only(self, make_account: MakeAccount) -> None:
        value = "credit"
        account = make_account(account_type=value)

        with pytest.raises(AttributeError):
            setattr(account, "account_type", "debit")


class TestBalance:
    def test_init(self, make_account: MakeAccount) -> None:
        value = 100
        expected = 10000
        account = make_account(account_balance=value)
        assert account.account_balance == expected

    def test_init_float(self, make_account: MakeAccount) -> None:
        value = 9.99
        expected = 999
        account = make_account(account_balance=value)
        assert account.account_balance == expected

    def test_init_negative(self, make_account: MakeAccount) -> None:
        value = -9.99
        with pytest.raises(ValidationError):
            make_account(account_balance=value)

    def test_is_read_only(self, make_account: MakeAccount) -> None:
        value = 100
        account = make_account(account_balance=value)

        with pytest.raises(AttributeError):
            setattr(account, "account_balance", 1234)

    def test_increase_account_balance(self, make_account: MakeAccount) -> None:
        value = 100
        account = make_account(account_balance=value)
        account.increase_balance(100)
        assert account.account_balance == 20000

    def test_increase_account_balance_float(self, make_account: MakeAccount) -> None:
        value = 9.97
        account = make_account(account_balance=value)
        account.increase_balance(5.67)
        assert account.account_balance == 1564

    def test_increase_account_balance_negative(self, make_account: MakeAccount) -> None:
        value = 9.97
        account = make_account(account_balance=value)
        with pytest.raises(ValidationError):
            account.increase_balance(-5.67)

    def test_decrease_account_balance(self, make_account: MakeAccount) -> None:
        value = 100
        account = make_account(account_balance=value)
        account.decrease_balance(50)
        assert account.account_balance == 5000

    def test_increase_decrease_balance_float(self, make_account: MakeAccount) -> None:
        value = 9.97
        account = make_account(account_balance=value)
        account.decrease_balance(5.67)
        assert account.account_balance == 430

    def test_increase_decrease_balance_negative(
        self, make_account: MakeAccount
    ) -> None:
        value = 9.97
        account = make_account(account_balance=value)
        with pytest.raises(ValidationError):
            account.decrease_balance(-5.67)

    def test_increase_decrease_balance_with_no_balance(
        self, make_account: MakeAccount
    ) -> None:
        value = 0
        account = make_account(account_balance=value)
        with pytest.raises(ValueError):
            account.decrease_balance(5.67)

    def test_is_not_new(self, make_account: MakeAccount) -> None:
        value = 100
        account = make_account(account_balance=value, is_new=False)
        assert account.account_balance == value


class TestFromRecord:
    def test(self) -> None:
        record = DBAccount(
            id=uuid.uuid4(),
            account_type="credit",
            account_number="1234",
            account_balance=10000,
            customer_id=uuid.uuid4(),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        account = Account.from_record(record)
        assert account.id == record.id
        assert account.customer_id == record.customer_id
        assert account.account_type == record.account_type
        assert account.account_number == record.account_number
        assert account.account_balance == record.account_balance
        assert account.created_at == record.created_at
        assert account.updated_at == record.updated_at
