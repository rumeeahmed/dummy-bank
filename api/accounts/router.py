from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status

from api import exceptions
from api.dependencies import AccountRepositoryDep, CustomerRepositoryDep, LoggerDep
from domain import Account
from repository import SearchCondition

from ..models import (
    AccountResponse,
    AccountsQueryParams,
    BalanceTransfer,
    BalanceUpdate,
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
    logger: LoggerDep,
    repository: AccountRepositoryDep,
    params: AccountsQueryParams = Depends(),
) -> PaginatedResponse:
    logger.info("retrieving accounts")

    paginated_accounts = await repository.load_paginated_accounts(
        page_size=params.page_size, page=params.page, customer_id=params.customer_id
    )

    logger.info(
        "retrieved accounts",
        n=len(paginated_accounts),
        total_count=paginated_accounts["total_count"],
        total_pages=paginated_accounts["total_pages"],
        page=paginated_accounts["page"],
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
    logger: LoggerDep,
    customer_repository: CustomerRepositoryDep,
    account_repository: AccountRepositoryDep,
    body: CreateAccount,
) -> AccountResponse:
    logger.info("retrieving customer", customer_id=body.customer_id)

    existing_customer = await customer_repository.load_customer_with_id(
        body.customer_id
    )

    if not existing_customer:
        logger.info("customer not found", customer_id=body.customer_id)
        raise exceptions.NotFoundError("customer not found")

    existing_account = await account_repository.load_account(
        SearchCondition(
            customer_id=body.customer_id,
            account_number=body.account_number,
            account_type=body.account_type,
        )
    )
    if existing_account:
        logger.info("account already exists", address_id=existing_account[0].id)
        raise exceptions.AlreadyExistsError("account already exists")

    account = Account(
        id=uuid4(),
        customer_id=existing_customer.id,
        account_number=body.account_number,
        account_type=body.account_type,
        account_balance=body.initial_balance,
        created_at=None,
        updated_at=None,
    )

    logger.info("saving account", account_id=account.id)

    await account_repository.save_account(account)
    return AccountResponse.model_validate(account)


@router.post(
    "/dummy-bank/v1/accounts/{account_id}/deposit",
    response_model=AccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Deposit money into Account",
)
async def deposit(
    logger: LoggerDep,
    repository: AccountRepositoryDep,
    account_id: UUID,
    body: BalanceUpdate,
) -> AccountResponse:
    logger.info("depositing amount", account_id=account_id, amount=body.amount)

    account = await repository.load_account_with_id(account_id)
    if not account:
        logger.info("account not found", account_id=account_id)
        raise exceptions.NotFoundError("account not found")

    account.increase_balance(body.amount)

    logger.info(
        "balance updated", account_id=account_id, balance=account.account_balance
    )
    await repository.save_account(account)

    return AccountResponse.model_validate(account)


@router.post(
    "/dummy-bank/v1/accounts/{account_id}/withdraw",
    response_model=AccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw money from Account",
)
async def withdraw(
    logger: LoggerDep,
    repository: AccountRepositoryDep,
    account_id: UUID,
    body: BalanceUpdate,
) -> AccountResponse:
    logger.info("withdrawing amount", account_id=account_id, amount=body.amount)

    account = await repository.load_account_with_id(account_id)
    if not account:
        logger.info("account not found", account_id=account_id)
        raise exceptions.NotFoundError("account not found")

    try:
        account.decrease_balance(body.amount)
        logger.info(
            "balance updated", account_id=account_id, balance=account.account_balance
        )
        await repository.save_account(account)
    except ValueError as e:
        logger.error(
            "failed to deposit money",
            account_id=account_id,
            amount=body.amount,
            error=str(e),
        )
        raise exceptions.InvalidRequestError(str(e))

    return AccountResponse.model_validate(account)


@router.post(
    "/dummy-bank/v1/accounts/{account_id}/transfer",
    response_model=list[AccountResponse],
    status_code=status.HTTP_200_OK,
    summary="Transfer money from Account",
)
async def transfer(
    logger: LoggerDep,
    repository: AccountRepositoryDep,
    account_id: UUID,
    body: BalanceTransfer,
) -> list[AccountResponse]:
    account = await repository.load_account_with_id(account_id)
    account_2 = await repository.load_account_with_id(body.account_id)
    if not account or not account_2:
        raise exceptions.NotFoundError("account not found")

    try:
        account.decrease_balance(body.amount)
        await repository.save_account(account)
        logger.info(
            "balance updated", account_id=account_id, balance=account.account_balance
        )
    except ValueError as e:
        logger.error(
            "failed to transfer money",
            account_id=account_id,
            amount=body.amount,
            error=str(e),
        )
        raise exceptions.InvalidRequestError(str(e))

    account_2.increase_balance(body.amount)
    await repository.save_account(account_2)
    logger.info(
        "balance updated", account_id=account_2.id, balance=account_2.account_balance
    )

    return [
        AccountResponse.model_validate(account),
        AccountResponse.model_validate(account_2),
    ]
