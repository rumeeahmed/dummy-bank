from uuid import uuid4

from fastapi import APIRouter, Depends, status

from api import exceptions
from api.dependencies import AccountRepositoryDep, CustomerRepositoryDep
from domain import Account

from ..models import (
    AccountResponse,
    AccountsQueryParams,
    CreateAccount,
    PaginatedResponse,
)

router = APIRouter(tags=["accounts"])


@router.get(
    "/dummy-bank/v1/accounts",
    response_model=PaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="List accounts for customer",
)
async def list_accounts(
    repository: AccountRepositoryDep, params: AccountsQueryParams = Depends()
) -> PaginatedResponse:
    paginated_accounts = await repository.load_paginated_accounts(
        page_size=params.page_size, page=params.page, customer_id=params.customer_id
    )
    return PaginatedResponse[AccountResponse](
        results=[
            AccountResponse.model_validate(customer)
            for customer in paginated_accounts["results"]
        ],
        total_count=paginated_accounts["total_count"],
        total_pages=paginated_accounts["total_pages"],
        page=paginated_accounts["page"],
        page_size=paginated_accounts["page_size"],
    )


@router.post(
    "/dummy-bank/v1/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Account",
)
async def create_account(
    customer_repository: CustomerRepositoryDep,
    account_repository: AccountRepositoryDep,
    body: CreateAccount,
) -> AccountResponse:
    existing_customer = await customer_repository.load_customer_with_id(
        body.customer_id
    )

    if not existing_customer:
        raise exceptions.NotFoundError("customer not found")

    print(existing_customer.id)
    account = Account(
        id=uuid4(),
        customer_id=existing_customer.id,
        account_number=body.account_number,
        account_type=body.account_type,
        account_balance=body.initial_balance,
        created_at=None,
        updated_at=None,
    )
    await account_repository.save_account(account)
    return AccountResponse.model_validate(account)
