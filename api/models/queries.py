from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationQueryParams(BaseModel):
    page: int = Field(Query(default=1, ge=1))
    page_size: int = Field(Query(default=50, ge=1, le=100))


class AccountsQueryParams(PaginationQueryParams):
    customer_id: UUID


class AddressesQueryParam(AccountsQueryParams): ...
