from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    NonNegativeInt,
)


class PaginatedResponse[T](BaseModel):
    results: list[T]
    page: int
    page_size: int
    total_count: int
    total_pages: int


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    account_balance: NonNegativeInt
    account_type: str
    account_number: str


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    display_address: str
    building_name: str | None
    building_number: str
    street: str
    town: str
    post_code: str
    county: str | None
    country: str
    latitude: str | None
    longitude: str | None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    middle_names: str | None
    last_name: str
    name: str | None
    email: EmailStr | None
    phone: str | None
    created_at: datetime
    updated_at: datetime
