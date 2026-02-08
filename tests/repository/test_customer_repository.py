import datetime
from typing import Callable
from uuid import UUID

import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime

from dummy_bank.domain import Customer
from dummy_bank.repository import CustomerRepository, SearchCondition


class TestLoadCustomerWithId:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        # Create and store the customer
        customer_id = UUID("b9448b6a-c470-45e7-8de0-6b926065cd40")
        customer = make_customer(
            id=customer_id,
            first_name="Bob",
            middle_names="Bobberson",
            last_name="Bobbington",
            email="bobby@example.com",
            phone="012345678",
        )
        await customer_repository.save_customer(customer)

        # Retrieve and check its values
        loaded = await customer_repository.load_customer_with_id(customer_id)

        assert loaded is not None
        assert loaded.id == customer.id
        assert loaded.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.first_name == customer.first_name
        assert loaded.middle_names == customer.middle_names
        assert loaded.last_name == customer.last_name
        assert loaded.email == customer.email
        assert loaded.phone == customer.phone

    @pytest.mark.asyncio
    async def test_does_not_exists(
        self, customer_repository: CustomerRepository
    ) -> None:
        customer_id = UUID("0a6f8e46-4e98-4ec5-a066-df1a18f8c9b3")
        loaded = await customer_repository.load_customer_with_id(customer_id)
        assert loaded is None


class TestSaveCustomer:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
    ) -> None:
        customer = make_customer()

        assert customer.created_at is None
        assert customer.updated_at is None

        # Save the customer in DB
        await customer_repository.save_customer(customer)
        loaded = await customer_repository.load_customer_with_id(customer.id)

        # Load it back out, timestamps should be populated
        assert loaded is not None
        assert loaded.id == customer.id
        assert loaded.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.first_name == customer.first_name
        assert loaded.middle_names == customer.middle_names
        assert loaded.last_name == customer.last_name
        assert loaded.email == customer.email
        assert loaded.phone == customer.phone


class TestLoadCustomer:
    @pytest.mark.parametrize(argnames="field", argvalues=["id", "email"])
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        customer_repository: CustomerRepository,
        make_customer: Callable[..., Customer],
        field: str,
    ) -> None:
        # Create the customer
        customer_id = "ff5efd4c-c13c-4787-8a62-2941c0a5553c"
        email = "test@example.com"
        customer = make_customer(id=customer_id, email=email)
        await customer_repository.save_customer(customer)

        # Choose the right search condition
        value = getattr(customer, field)
        condition = SearchCondition.model_validate({field: value})

        # Check the values
        loaded = await customer_repository.load_customer(search_condition=condition)

        assert loaded is not None
        assert loaded.id == customer.id
        assert loaded.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.first_name == customer.first_name
        assert loaded.middle_names == customer.middle_names
        assert loaded.last_name == customer.last_name
        assert loaded.email == customer.email
        assert loaded.phone == customer.phone

    @pytest.mark.parametrize(
        "field, value",
        [
            ("id", "ff5efd4c-c13c-4787-8a62-2941c0a5553c"),
            ("email", "test@example.com"),
        ],
    )
    @pytest.mark.asyncio
    async def test_does_not_exists(
        self,
        customer_repository: CustomerRepository,
        field: str,
        value: str,
        make_customer: Callable[..., Customer],
    ) -> None:
        # Add some noise to the DB.
        customer = make_customer(
            id="4499599e-b25d-488b-b581-d6979837ac21",
            email="noise@example.com",
        )
        await customer_repository.save_customer(customer)

        # Search DB with non-existent values.
        condition = SearchCondition.model_validate({field: value})
        loaded = await customer_repository.load_customer(search_condition=condition)
        assert loaded is None
