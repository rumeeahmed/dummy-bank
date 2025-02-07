import datetime
from typing import Callable
from uuid import UUID

import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime
from sqlalchemy.exc import IntegrityError

from domain import Address, Customer
from repository import (
    AddressesRepository,
    CustomerRepository,
    SearchCondition,
)


class TestLoadAddressWithId:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        addresses_repository: AddressesRepository,
        customer_repository: CustomerRepository,
        make_address: Callable[..., Address],
        make_customer: Callable[..., Customer],
    ) -> None:
        # Create and store the customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        address = make_address(customer_id=customer.id)
        await addresses_repository.save_address(address)

        # Retrieve and check its values
        loaded = await addresses_repository.load_address_with_id(address.id)

        assert loaded is not None
        assert loaded.id == address.id
        assert loaded.customer_id == address.customer_id
        assert customer.id == address.customer_id
        assert loaded.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.building_name == address.building_name
        assert loaded.building_number == address.building_number
        assert loaded.street == address.street
        assert loaded.town == address.town
        assert loaded.post_code == address.post_code
        assert loaded.county == address.county
        assert loaded.country == address.country
        assert loaded.latitude == address.latitude
        assert loaded.longitude == address.longitude

    @pytest.mark.asyncio
    async def test_does_not_exists(
        self, addresses_repository: AddressesRepository
    ) -> None:
        address_id = UUID("0a6f8e46-4e98-4ec5-a066-df1a18f8c9b3")
        loaded = await addresses_repository.load_address_with_id(address_id)
        assert loaded is None


class TestLoadAddressWithCustomerId:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        addresses_repository: AddressesRepository,
        customer_repository: CustomerRepository,
        make_address: Callable[..., Address],
        make_customer: Callable[..., Customer],
    ) -> None:
        # Create and store the customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        address = make_address(customer_id=customer.id)
        await addresses_repository.save_address(address)

        address2 = make_address(customer_id=customer.id)
        await addresses_repository.save_address(address2)

        address3 = make_address(customer_id=customer.id)
        await addresses_repository.save_address(address3)

        customer2 = make_customer()
        await customer_repository.save_customer(customer2)

        address4 = make_address(customer_id=customer2.id)
        await addresses_repository.save_address(address4)

        # Retrieve and check its values
        loaded = await addresses_repository.load_addresses_with_customer_id(customer.id)
        assert loaded is not None
        assert len(loaded) == 3

        loaded2 = await addresses_repository.load_addresses_with_customer_id(
            customer2.id
        )
        assert loaded2 is not None
        assert len(loaded2) == 1

    @pytest.mark.asyncio
    async def test_does_not_exists(
        self, addresses_repository: AddressesRepository
    ) -> None:
        customer_id = UUID("0a6f8e46-4e98-4ec5-a066-df1a18f8c9b3")
        loaded = await addresses_repository.load_addresses_with_customer_id(customer_id)
        assert loaded is None


class TestSaveAddress:
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test(
        self,
        addresses_repository: AddressesRepository,
        customer_repository: CustomerRepository,
        make_address: Callable[..., Address],
        make_customer: Callable[..., Customer],
    ) -> None:
        # Address needs a customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        address = make_address(customer_id=customer.id)
        await addresses_repository.save_address(address)

        # Load it back out, timestamps should be populated
        loaded = await addresses_repository.load_address_with_id(address.id)

        assert loaded is not None
        assert loaded.id == address.id
        assert loaded.customer_id == address.customer_id
        assert customer.id == address.customer_id
        assert loaded.created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded.building_name == address.building_name
        assert loaded.building_number == address.building_number
        assert loaded.street == address.street
        assert loaded.town == address.town
        assert loaded.post_code == address.post_code
        assert loaded.county == address.county
        assert loaded.country == address.country
        assert loaded.latitude == address.latitude
        assert loaded.longitude == address.longitude

    @pytest.mark.asyncio
    async def test_save_address_with_missing_customer(
        self,
        addresses_repository: AddressesRepository,
        customer_repository: CustomerRepository,
        make_address: Callable[..., Address],
        make_customer: Callable[..., Customer],
    ) -> None:
        address = make_address()
        with pytest.raises(IntegrityError):
            await addresses_repository.save_address(address)


class TestLoadAddresses:
    @pytest.mark.parametrize(argnames="field", argvalues=["id"])
    @pytest.mark.asyncio
    @freeze_time("2018-11-13T15:16:08")
    async def test_exists(
        self,
        addresses_repository: AddressesRepository,
        customer_repository: CustomerRepository,
        make_address: Callable[..., Address],
        make_customer: Callable[..., Customer],
        field: str,
    ) -> None:
        # Create the customer
        customer = make_customer()
        await customer_repository.save_customer(customer)

        address = make_address(customer_id=customer.id)
        await addresses_repository.save_address(address)

        # Choose the right search condition
        if field == "customer_id":
            value = getattr(customer, "id")
        else:
            value = getattr(address, field)

        condition = SearchCondition.model_validate({field: value})

        # Check the values
        loaded = await addresses_repository.load_address(search_condition=condition)

        assert loaded is not None
        assert len(loaded) == 1

        assert loaded is not None
        assert loaded[0].id == address.id
        assert loaded[0].customer_id == address.customer_id
        assert customer.id == address.customer_id
        assert loaded[0].created_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded[0].updated_at == FakeDatetime(
            2018, 11, 13, 15, 16, 8, tzinfo=datetime.timezone.utc
        )
        assert loaded[0].building_name == address.building_name
        assert loaded[0].building_number == address.building_number
        assert loaded[0].street == address.street
        assert loaded[0].town == address.town
        assert loaded[0].post_code == address.post_code
        assert loaded[0].county == address.county
        assert loaded[0].country == address.country
        assert loaded[0].latitude == address.latitude
        assert loaded[0].longitude == address.longitude

    @pytest.mark.parametrize(
        "field, value",
        [
            ("id", "ff5efd4c-c13c-4787-8a62-2941c0a5553c"),
            ("customer_id", "ff5efd4c-c13c-4787-8a62-2941c0a5553c"),
        ],
    )
    @pytest.mark.asyncio
    async def test_does_not_exists(
        self, addresses_repository: AddressesRepository, field: str, value: str
    ) -> None:
        condition = SearchCondition.model_validate({field: value})
        loaded = await addresses_repository.load_address(search_condition=condition)
        assert loaded is None
