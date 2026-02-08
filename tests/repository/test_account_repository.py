import datetime
from uuid import UUID

import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime
from sqlalchemy.exc import IntegrityError

from dummy_bank.repository import (
    AccountsRepository,
    CustomerRepository,
    SearchCondition,
)

from ..make_domain_objects import MakeAccount, MakeCustomer


class TestLoadAccountWithId:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: MakeAccount,
        make_customer: MakeCustomer,
    ) -> None:
        # Create and store the customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(customer_id=customer.id)
        await account_repository.save_account(account)

        # Retrieve and check its values
        loaded = await account_repository.load_account_with_id(account.id)

        assert loaded is not None
        assert loaded.id == account.id
        assert loaded.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.account_type == account.account_type
        assert loaded.account_number == account.account_number
        assert loaded.customer_id == account.customer_id
        assert loaded.customer_id == customer.id
        assert loaded.account_balance == account.account_balance

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
        make_account: MakeAccount,
        make_customer: MakeCustomer,
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

        loaded2 = await account_repository.load_account_with_customer_id(customer2.id)
        assert loaded2 is not None
        assert len(loaded2) == 1

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
        make_account: MakeAccount,
        make_customer: MakeCustomer,
    ) -> None:
        # Account needs a customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        account = make_account(customer_id=customer.id)
        await account_repository.save_account(account)

        # Load it back out, timestamps should be populated
        loaded = await account_repository.load_account_with_id(account.id)

        assert loaded is not None
        assert loaded.id == account.id
        assert loaded.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.account_type == account.account_type
        assert loaded.account_number == account.account_number
        assert loaded.customer_id == account.customer_id
        assert loaded.customer_id == customer.id
        assert loaded.account_balance == account.account_balance

    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_update_balance(
        self,
        account_repository: AccountsRepository,
        customer_repository: CustomerRepository,
        make_account: MakeAccount,
        make_customer: MakeCustomer,
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
        make_account: MakeAccount,
        make_customer: MakeCustomer,
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
        make_account: MakeAccount,
        make_customer: MakeCustomer,
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

        assert loaded[0].id == account.id
        assert loaded[0].created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded[0].updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded[0].account_type == account.account_type
        assert loaded[0].account_number == account.account_number
        assert loaded[0].customer_id == account.customer_id
        assert loaded[0].customer_id == customer.id
        assert loaded[0].account_balance == account.account_balance

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
