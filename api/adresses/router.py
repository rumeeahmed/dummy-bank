from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status

from api import exceptions
from api.dependencies import AddressesRepositoryDep, CustomerRepositoryDep, SettingsDep
from domain import Address

from ..models import (
    AddressesQueryParam,
    AddressResponse,
    CreateAddress,
    PaginatedResponse,
    UpdateAddress,
)

router = APIRouter(tags=["addresses"])


@router.get(
    "/dummy-bank/v1/addresses",
    response_model=PaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="List addresses for customer",
)
async def list_addresses(
    repository: AddressesRepositoryDep, params: AddressesQueryParam = Depends()
) -> PaginatedResponse:
    paginated_addresses = await repository.load_paginated_addresses(
        page_size=params.page_size, page=params.page, customer_id=params.customer_id
    )
    return PaginatedResponse[AddressResponse](
        results=[
            AddressResponse.model_validate(customer)
            for customer in paginated_addresses["results"]
        ],
        total_count=paginated_addresses["total_count"],
        total_pages=paginated_addresses["total_pages"],
        page=paginated_addresses["page"],
        page_size=paginated_addresses["page_size"],
    )


@router.post(
    "/dummy-bank/v1/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Address",
)
async def create_address(
    settings: SettingsDep,
    customer_repository: CustomerRepositoryDep,
    addresses_repository: AddressesRepositoryDep,
    body: CreateAddress,
) -> AddressResponse:
    existing_customer = await customer_repository.load_customer_with_id(
        body.customer_id
    )

    if not existing_customer:
        raise exceptions.NotFoundError("customer not found")

    address = Address(
        id=uuid4(),
        customer_id=existing_customer.id,
        building_name=body.building_name,
        building_number=body.building_number,
        street=body.street,
        town=body.town,
        post_code=body.post_code,
        county=body.county,
        country=body.country,
        longitude=None,
        latitude=None,
        created_at=None,
        updated_at=None,
    )

    try:
        coordinates = await settings.google_maps_client().get_coordinates(
            address.display_address
        )
        address.latitude = coordinates.latitude if coordinates else None
        address.longitude = coordinates.longitude if coordinates else None

    except Exception:
        pass

    await addresses_repository.save_address(address)
    return AddressResponse.model_validate(address)


@router.patch(
    "/dummy-bank/v1/addresses/{address_id}",
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Address",
)
async def update_address(
    settings: SettingsDep,
    address_id: UUID,
    addresses_repository: AddressesRepositoryDep,
    body: UpdateAddress,
) -> AddressResponse:
    existing = await addresses_repository.load_address_with_id(id=address_id)

    if not existing:
        raise exceptions.NotFoundError("address not found")

    to_update = body.model_dump(exclude_unset=True)

    if "building_name" in to_update:
        existing.building_name = to_update["building_name"]

    if "building_number" in to_update:
        existing.building_number = to_update["building_number"]

    if "street" in to_update:
        existing.street = to_update["street"]

    if "town" in to_update:
        existing.town = to_update["town"]

    if "post_code" in to_update:
        existing.post_code = to_update["post_code"]

    if "county" in to_update:
        existing.county = to_update["county"]

    if "country" in to_update:
        existing.country = to_update["country"]

    try:
        coordinates = await settings.google_maps_client().get_coordinates(
            existing.display_address
        )
        existing.latitude = coordinates.latitude if coordinates else None
        existing.longitude = coordinates.longitude if coordinates else None

    except Exception:
        pass

    await addresses_repository.save_address(existing)
    return AddressResponse.model_validate(existing)
