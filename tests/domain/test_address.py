from datetime import datetime, timezone
from typing import Callable
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from domain import Address
from repository import DBAddress


class TestID:
    def test_init_valid(self, make_address: Callable[..., Address]) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        address = make_address(id=value)
        assert address.id == value

    def test_is_read_only(self, make_address: Callable[..., Address]) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        address = make_address(id=value)

        with pytest.raises(AttributeError):
            address.id = UUID("c668e0af-d1b9-412f-a1da-790e5905da26")  # type: ignore[misc]


class TestCustomerID:
    def test_init_valid(self, make_address: Callable[..., Address]) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        address = make_address(customer_id=value)
        assert address.customer_id == value

    def test_is_read_only(self, make_address: Callable[..., Address]) -> None:
        value = UUID("be8f74c0-c7ff-4bd1-9d5b-6e224d6ce6bc")
        address = make_address(customer_id=value)

        with pytest.raises(AttributeError):
            address.customer_id = UUID("c668e0af-d1b9-412f-a1da-790e5905da26")  # type: ignore[misc]


class TestCreatedAt:
    VALID_VALUES = [None, datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: datetime | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(created_at=value)
        assert address.created_at == value

    def test_is_settable_if_none(self, make_address: Callable[..., Address]) -> None:
        address = make_address(created_at=None)
        address.created_at = datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)
        assert address.created_at == datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)

    def test_is_read_only_if_not_none(
        self, make_address: Callable[..., Address]
    ) -> None:
        value = datetime(2024, 6, 26, 1, 2, 3, 4, tzinfo=timezone.utc)
        address = make_address(created_at=value)

        with pytest.raises(AttributeError):
            address.created_at = datetime.now(timezone.utc)

        assert address.created_at == value


class TestUpdatedAt:
    VALID_VALUES = [None, datetime(2024, 8, 15, 16, 0, tzinfo=timezone.utc)]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: datetime | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(updated_at=value)
        assert address.updated_at == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: datetime | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(updated_at=None)
        address.updated_at = value
        assert address.updated_at == value


class TestBuildingName:
    VALID_VALUES = [None, "Building Name"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(building_name=value)
        assert address.building_name == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address()
        address.building_name = value
        assert address.building_name == value


class TestBuildingNumber:
    VALID_VALUES = ["146"]
    INVALID_VALUES = [None]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(building_number=value)
        assert address.building_number == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(self, value: str, make_address: Callable[..., Address]) -> None:
        address = make_address()
        address.building_number = value
        assert address.building_number == value

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_init_invalid(
        self, value: None, make_address: Callable[..., Address]
    ) -> None:
        with pytest.raises(ValidationError):
            make_address(building_number=value)


class TestStreet:
    VALID_VALUES = ["My Street"]
    INVALID_VALUES = [None]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(street=value)
        assert address.street == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(self, value: str, make_address: Callable[..., Address]) -> None:
        address = make_address()
        address.street = value
        assert address.street == value

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_init_invalid(
        self, value: None, make_address: Callable[..., Address]
    ) -> None:
        with pytest.raises(ValidationError):
            make_address(street=value)


class TestTown:
    VALID_VALUES = ["Luton"]
    INVALID_VALUES = [None]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(town=value)
        assert address.town == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(self, value: str, make_address: Callable[..., Address]) -> None:
        address = make_address()
        address.town = value
        assert address.town == value

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_init_invalid(
        self, value: None, make_address: Callable[..., Address]
    ) -> None:
        with pytest.raises(ValidationError):
            make_address(town=value)


class TestPostCode:
    VALID_VALUES = ["LU1 JHS"]
    INVALID_VALUES = [None]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(post_code=value)
        assert address.post_code == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(self, value: str, make_address: Callable[..., Address]) -> None:
        address = make_address()
        address.post_code = value
        assert address.post_code == value

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_init_invalid(
        self, value: None, make_address: Callable[..., Address]
    ) -> None:
        with pytest.raises(ValidationError):
            make_address(post_code=value)


class TestCounty:
    VALID_VALUES = [None, "Bedfordshire"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(county=value)
        assert address.county == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address()
        address.county = value
        assert address.county == value


class TestCountry:
    VALID_VALUES = ["England"]
    INVALID_VALUES = [None]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(country=value)
        assert address.country == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(self, value: str, make_address: Callable[..., Address]) -> None:
        address = make_address()
        address.country = value
        assert address.country == value

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_init_invalid(
        self, value: None, make_address: Callable[..., Address]
    ) -> None:
        with pytest.raises(ValidationError):
            make_address(country=value)


class TestLatitude:
    VALID_VALUES = [None, "245"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(latitude=value)
        assert address.latitude == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address()
        address.latitude = value
        assert address.latitude == value


class TestLongitude:
    VALID_VALUES = [None, "334"]

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_init_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address(longitude=value)
        assert address.longitude == value

    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_set_valid(
        self, value: str | None, make_address: Callable[..., Address]
    ) -> None:
        address = make_address()
        address.longitude = value
        assert address.longitude == value


class TestDisplayAddress:
    @pytest.mark.parametrize(
        argnames=[
            "building_name",
            "building_number",
            "street",
            "post_code",
            "town",
            "county",
            "country",
            "expected",
        ],
        argvalues=[
            pytest.param(
                "My Building",
                "146",
                "Cool Road",
                "LU2 4HQ",
                "Luton",
                "Bedfordshire",
                "England",
                "My Building, 146, Cool Road, Luton, Bedfordshire, LU2 4HQ, England",
                id="all address values included",
            ),
            pytest.param(
                None,
                "146",
                "Cool Road",
                "LU2 4HQ",
                "Luton",
                "Bedfordshire",
                "England",
                "146, Cool Road, Luton, Bedfordshire, LU2 4HQ, England",
                id="missing building name",
            ),
            pytest.param(
                "My Building",
                "146",
                "Cool Road",
                "LU2 4HQ",
                "Luton",
                None,
                "England",
                "My Building, 146, Cool Road, Luton, LU2 4HQ, England",
                id="missing county",
            ),
            pytest.param(
                None,
                "146",
                "Cool Road",
                "LU2 4HQ",
                "Luton",
                None,
                "England",
                "146, Cool Road, Luton, LU2 4HQ, England",
                id="missing building name and county",
            ),
        ],
    )
    def test(
        self,
        building_name: str | None,
        building_number: str,
        street: str,
        post_code: str,
        town: str,
        county: str | None,
        country: str,
        expected: str,
        make_address: Callable[..., Address],
    ) -> None:
        address = make_address(
            building_name=building_name,
            building_number=building_number,
            street=street,
            post_code=post_code,
            county=county,
            country=country,
            town=town,
        )
        assert address.display_address == expected


class TestFromRecord:
    def test(self) -> None:
        record = DBAddress(
            id=uuid4(),
            customer_id=uuid4(),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
            building_name="My House",
            building_number="12345",
            street="Some Street",
            town="Some Town",
            county="Some County",
            post_code="Some Postcode",
            country="Some Country",
            latitude="123.456",
            longitude="123.456",
        )

        address = Address.from_record(record)
        assert address.id == record.id
        assert address.customer_id == record.customer_id
        assert address.created_at == record.created_at
        assert address.updated_at == record.updated_at
        assert address.building_name == record.building_name
        assert address.building_number == record.building_number
        assert address.street == record.street
        assert address.town == record.town
        assert address.county == record.county
        assert address.post_code == record.post_code
        assert address.country == record.country
        assert address.latitude == record.latitude
        assert address.longitude == record.longitude
