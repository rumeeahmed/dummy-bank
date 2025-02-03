from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status

from api import exceptions
from api.dependencies import CustomerRepositoryDep
from domain import Customer
from repository import SearchCondition

from .models import (
    CreateCustomer,
    CustomerResponse,
    PaginatedResponse,
    PaginationQueryParams,
    UpdateCustomer,
)

router = APIRouter(tags=["customer"])


@router.get(
    "/dummy-bank/v1/customer",
    response_model=PaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="List customers",
)
async def list_customers(
    repository: CustomerRepositoryDep, params: PaginationQueryParams = Depends()
) -> PaginatedResponse:
    paginated_customers = await repository.load_paginated_customers(
        page_size=params.page_size, page=params.page
    )
    return PaginatedResponse[CustomerResponse](
        results=[
            CustomerResponse.model_validate(customer)
            for customer in paginated_customers["results"]
        ],
        total_count=paginated_customers["total_count"],
        total_pages=paginated_customers["total_pages"],
        page=paginated_customers["page"],
        page_size=paginated_customers["page_size"],
    )


@router.get(
    "/dummy-bank/v1/customer/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a customer by id",
)
async def get_customer_by_id(
    repository: CustomerRepositoryDep, customer_id: UUID
) -> CustomerResponse:
    customer = await repository.load_customer_with_id(customer_id)

    if not customer:
        raise exceptions.NotFoundError("customer not found")

    return CustomerResponse.model_validate(customer)


@router.post(
    "/dummy-bank/v1/customer",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Customer",
)
async def create_customer(
    repository: CustomerRepositoryDep, body: CreateCustomer
) -> CustomerResponse:
    existing_customer = await repository.load_customer(
        SearchCondition(email=body.email)
    )

    if existing_customer:
        raise exceptions.AlreadyExistsError("customer already exists")

    customer = Customer(
        id=uuid4(),
        email=body.email,
        first_name=body.first_name,
        middle_names=body.middle_names,
        last_name=body.last_name,
        phone=body.phone,
        created_at=None,
        updated_at=None,
    )
    await repository.save_customer(customer)
    return CustomerResponse.model_validate(customer)


@router.patch(
    "/dummy-bank/v1/customer/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a Customer",
)
async def update_application(
    repository: CustomerRepositoryDep, customer_id: UUID, body: UpdateCustomer
) -> CustomerResponse:
    existing = await repository.load_customer_with_id(customer_id)

    if existing is None:
        raise exceptions.NotFoundError("customer not found")

    to_update = body.model_dump(exclude_unset=True)

    if "first_name" in to_update:
        existing.first_name = to_update["first_name"]

    if "middle_names" in to_update:
        existing.middle_names = to_update["middle_names"]

    if "last_name" in to_update:
        existing.last_name = to_update["last_name"]

    if "phone" in to_update:
        existing.phone = to_update["phone"]

    if "email" in to_update:
        existing.email = to_update["email"]

    await repository.save_customer(existing)
    return CustomerResponse.model_validate(existing)
