from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select

from domain import Address

from .db_address import DBAddress
from .repository import Repository
from .search_condition import SearchCondition


class AddressesRepository(Repository):
    async def save_address(self, address: Address) -> None:
        now = datetime.now(timezone.utc)
        address.updated_at = now

        try:
            address.created_at = now
        except AttributeError:
            pass

        record = DBAddress(
            id=address.id,
            customer_id=address.customer_id,
            created_at=address.created_at,
            updated_at=address.updated_at,
            building_name=address.building_name,
            building_number=address.building_number,
            street=address.street,
            town=address.town,
            post_code=address.post_code,
            county=address.county,
            country=address.country,
            latitude=address.latitude,
            longitude=address.longitude,
        )

        async with self._session() as session:
            await session.merge(record)
            await session.commit()

    async def load_address(
        self, search_condition: SearchCondition
    ) -> list[Address] | None:
        stmt = select(DBAddress).filter_by(**search_condition.as_filter_by_kwargs())

        async with self._session() as session:
            results = (await session.scalars(stmt)).all()

        if not results:
            return None

        return [Address.from_record(record) for record in results]

    async def load_address_with_id(self, id: UUID) -> Address | None:
        condition = SearchCondition(id=id)
        addresses = await self.load_address(search_condition=condition)
        return addresses[0] if addresses else None

    async def load_addresses_with_customer_id(
        self, customer_id: UUID
    ) -> list[Address] | None:
        condition = SearchCondition(customer_id=customer_id)
        return await self.load_address(search_condition=condition)

    async def load_paginated_addresses(
        self, page: int, page_size: int, customer_id: UUID
    ) -> dict[str, Any]:
        offset = (page - 1) * page_size
        count = await self.get_count(DBAddress, customer_id=customer_id)
        total_pages = (count + page_size - 1) // page_size

        stmt = (
            select(DBAddress)
            .filter_by(customer_id=customer_id)
            .limit(page_size)
            .offset(offset)
        )

        async with self._session() as session:
            results = (await session.scalars(stmt)).all()

        return {
            "results": [Address.from_record(record) for record in results],
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": count,
        }
