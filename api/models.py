from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from fastapi import Query
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
)

T = TypeVar("T")


class PaginationQueryParams(BaseModel):
    page: int = Field(Query(default=1, ge=1))
    page_size: int = Field(Query(default=50, ge=1, le=100))


class PaginatedResponse(BaseModel, Generic[T]):
    results: list[T]
    page: int
    page_size: int
    total_count: int
    total_pages: int


class UpdateCustomer(BaseModel):
    first_name: str | None = None
    middle_names: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class CreateCustomer(BaseModel):
    first_name: str
    middle_names: str | None = None
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None


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


class AccountsQueryParams(PaginationQueryParams):
    customer_id: UUID


class CreateAccount(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: UUID
    account_type: str
    account_number: str
    initial_balance: NonNegativeFloat


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    account_balance: NonNegativeInt
    account_type: str
    account_number: str


class BalanceUpdate(BaseModel):
    amount: NonNegativeFloat


class TransferBalance(BalanceUpdate):
    account_id: UUID
