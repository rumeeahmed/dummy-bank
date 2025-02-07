from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    NonNegativeFloat,
)


class CreateCustomer(BaseModel):
    first_name: str
    middle_names: str | None = None
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None


class UpdateCustomer(BaseModel):
    first_name: str | None = None
    middle_names: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class CreateAccount(BaseModel):
    customer_id: UUID
    account_type: str
    account_number: str
    initial_balance: NonNegativeFloat


class BalanceUpdate(BaseModel):
    amount: NonNegativeFloat


class BalanceTransfer(BalanceUpdate):
    account_id: UUID


class UpdateAddress(BaseModel):
    building_name: str | None = None
    building_number: str | None = None
    street: str | None = None
    town: str | None = None
    post_code: str | None = None
    county: str | None = None
    country: str | None = None


class CreateAddress(BaseModel):
    customer_id: UUID
    building_name: str | None
    building_number: str
    street: str
    town: str
    post_code: str
    county: str | None
    country: str
