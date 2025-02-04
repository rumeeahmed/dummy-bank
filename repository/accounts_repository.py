from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select

from domain import Account

from .db_account import DBAccount
from .repository import Repository
from .search_condition import SearchCondition


class AccountsRepository(Repository):
    async def save_account(self, account: Account) -> None:
        now = datetime.now(timezone.utc)
        account.updated_at = now

        try:
            account.created_at = now
        except AttributeError:
            pass

        record = DBAccount(
            id=account.id,
            customer_id=account.customer_id,
            created_at=account.created_at,
            updated_at=account.updated_at,
            account_type=account.account_type,
            account_number=account.account_number,
            account_balance=account.account_balance,
        )

        async with self._session() as session:
            await session.merge(record)
            await session.commit()

    async def load_account(
        self, search_condition: SearchCondition
    ) -> list[Account] | None:
        stmt = select(DBAccount).filter_by(**search_condition.as_filter_by_kwargs())

        async with self._session() as session:
            results = (await session.scalars(stmt)).all()

        if not results:
            return None

        return [Account.from_record(record) for record in results]

    async def load_account_with_id(self, id: UUID) -> Account | None:
        condition = SearchCondition(id=id)
        accounts = await self.load_account(search_condition=condition)
        return accounts[0] if accounts else None

    async def load_account_with_customer_id(
        self, customer_id: UUID
    ) -> list[Account] | None:
        condition = SearchCondition(customer_id=customer_id)
        return await self.load_account(search_condition=condition)

    async def load_paginated_accounts(
        self, page: int, page_size: int, customer_id: UUID
    ) -> dict[str, Any]:
        offset = (page - 1) * page_size
        count = await self.get_count(DBAccount, customer_id=customer_id)
        total_pages = (count + page_size - 1) // page_size

        stmt = (
            select(DBAccount)
            .filter_by(customer_id=customer_id)
            .limit(page_size)
            .offset(offset)
        )

        async with self._session() as session:
            results = (await session.scalars(stmt)).all()

        return {
            "results": [Account.from_record(record) for record in results],
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": count,
        }
