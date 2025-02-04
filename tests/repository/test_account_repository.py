import datetime
from typing import Callable
from uuid import UUID

import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime
from sqlalchemy.exc import IntegrityError

from domain import Account, Customer
from repository import AccountsRepository, CustomerRepository, SearchCondition


class TestLoadAccountWithId:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: Callable[..., Account],
        make_customer: Callable[..., Customer],
    ) -> None:
        # Create and store the customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(customer_id=customer.id)
        await account_repository.save_account(account)

        # Retrieve and check its values
        loaded = await account_repository.load_account_with_id(account.id)

        assert loaded is not None
        assert account.id == loaded.id
        assert account.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert customer.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert account.account_type == loaded.account_type
        assert account.account_number == loaded.account_number
        assert account.customer_id == customer.id
        assert account.account_balance == loaded.account_balance

    @pytest.mark.asyncio
    async def test_does_not_exists(
        self, account_repository: AccountsRepository
    ) -> None:
        account_id = UUID("0a6f8e46-4e98-4ec5-a066-df1a18f8c9b3")
        loaded = await account_repository.load_account_with_id(account_id)
        assert loaded is None


class TestLoadAccountWithCustomerId:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: Callable[..., Account],
        make_customer: Callable[..., Customer],
    ) -> None:
        # Create and store the customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(customer_id=customer.id)
        await account_repository.save_account(account)

        account2 = make_account(customer_id=customer.id)
        await account_repository.save_account(account2)

        account3 = make_account(customer_id=customer.id)
        await account_repository.save_account(account3)

        customer2 = make_customer()
        await customer_repository.save_customer(customer2)

        account4 = make_account(customer_id=customer2.id)
        await account_repository.save_account(account4)

        # Retrieve and check its values
        loaded = await account_repository.load_account_with_customer_id(customer.id)
        assert loaded is not None
        assert len(loaded) == 3

    @pytest.mark.asyncio
    async def test_does_not_exists(
        self, account_repository: AccountsRepository
    ) -> None:
        customer_id = UUID("0a6f8e46-4e98-4ec5-a066-df1a18f8c9b3")
        loaded = await account_repository.load_account_with_customer_id(customer_id)
        assert loaded is None


class TestSaveAccount:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: Callable[..., Account],
        make_customer: Callable[..., Customer],
    ) -> None:
        # Account needs a customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(customer_id=customer.id)
        await account_repository.save_account(account)

        # Load it back out, timestamps should be populated
        loaded = await account_repository.load_account_with_id(account.id)

        assert loaded is not None
        assert account.id == loaded.id
        assert account.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert account.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert account.account_type == loaded.account_type
        assert account.account_number == loaded.account_number
        assert account.customer_id == customer.id
        assert account.account_balance == loaded.account_balance

    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_update_balance(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: Callable[..., Account],
        make_customer: Callable[..., Customer],
    ) -> None:
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(customer_id=customer.id)
        await account_repository.save_account(account)

        loaded = await account_repository.load_account_with_id(account.id)
        assert loaded is not None
        assert account.account_balance == loaded.account_balance

        loaded.increase_balance(500)
        await account_repository.save_account(loaded)

        loaded2 = await account_repository.load_account_with_id(loaded.id)
        assert loaded2 is not None
        assert loaded.account_balance == loaded2.account_balance
        assert loaded2.account_balance != account.account_balance

    @pytest.mark.asyncio
    async def test_save_account_with_missing_customer(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: Callable[..., Account],
        make_customer: Callable[..., Customer],
    ) -> None:
        account = make_account()
        with pytest.raises(IntegrityError):
            await account_repository.save_account(account)


class TestLoadAccount:
    @pytest.mark.parametrize(argnames="field", argvalues=["id"])
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: Callable[..., Account],
        make_customer: Callable[..., Customer],
        field: str,
    ) -> None:
        # Create the customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(customer_id=customer.id)
        await account_repository.save_account(account)

        # Choose the right search condition
        if field == "customer_id":
            value = getattr(customer, "id")
        else:
            value = getattr(account, field)

        condition = SearchCondition.model_validate({field: value})

        # Check the values
        loaded = await account_repository.load_account(search_condition=condition)

        assert loaded is not None
        assert len(loaded) == 1

        assert account.id == loaded[0].id
        assert account.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert customer.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert account.account_type == loaded[0].account_type
        assert account.account_number == loaded[0].account_number
        assert account.account_balance == loaded[0].account_balance
        assert account.customer_id == loaded[0].customer_id
        assert account.customer_id == customer.id

    @pytest.mark.parametrize(
        "field, value",
        [
            ("id", "ff5efd4c-c13c-4787-8a62-2941c0a5553c"),
            ("customer_id", "ff5efd4c-c13c-4787-8a62-2941c0a5553c"),
        ],
    )
    @pytest.mark.asyncio
    async def test_does_not_exists(
        self, account_repository: AccountsRepository, field: str, value: str
    ) -> None:
        condition = SearchCondition.model_validate({field: value})
        loaded = await account_repository.load_account(search_condition=condition)
        assert loaded is None
