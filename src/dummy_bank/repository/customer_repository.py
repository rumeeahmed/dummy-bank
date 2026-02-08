from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select

from dummy_bank.domain import Customer

from .db_customer import DBCustomer
from .repository import Repository
from .search_condition import SearchCondition


class CustomerRepository(Repository):
    async def save_customer(self, customer: Customer) -> None:
        now = datetime.now(timezone.utc)
        customer.updated_at = now

        try:
            customer.created_at = now
        except AttributeError:
            pass

        record = DBCustomer(
            id=customer.id,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            first_name=customer.first_name,
            middle_names=customer.middle_names,
            last_name=customer.last_name,
            email=customer.email,
            phone=customer.phone,
        )

        async with self._session() as session:
            await session.merge(record)
            await session.commit()

    async def load_customer(self, search_condition: SearchCondition) -> Customer | None:
        stmt = select(DBCustomer).filter_by(**search_condition.as_filter_by_kwargs())

        async with self._session() as session:
            results = (await session.scalars(stmt)).all()

        if not results:
            return None

        record = results[0]

        return Customer.from_record(record)

    async def load_customer_with_id(self, id: UUID) -> Customer | None:
        condition = SearchCondition(id=id)
        return await self.load_customer(search_condition=condition)

    async def load_paginated_customers(
        self, page: int, page_size: int
    ) -> dict[str, Any]:
        offset = (page - 1) * page_size
        count = await self.get_count(DBCustomer)
        total_pages = (count + page_size - 1) // page_size

        stmt = select(DBCustomer).limit(page_size).offset(offset)
        async with self._session() as session:
            results = (await session.scalars(stmt)).all()

        return {
            "results": [Customer.from_record(record) for record in results],
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": count,
        }
