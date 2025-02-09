from datetime import datetime
from decimal import Decimal
from typing import Any, Self
from uuid import UUID

from pydantic import NonNegativeFloat, NonNegativeInt, validate_call


class Account:
    @validate_call
    def __init__(
        self,
        *,
        id: UUID,
        created_at: datetime | None,
        updated_at: datetime | None,
        account_type: str,
        account_number: str,
        account_balance: NonNegativeFloat,
        customer_id: UUID,
        is_new: bool = True,
    ) -> None:
        self._id = id
        self._created_at = created_at
        self.updated_at = updated_at
        self._account_type = account_type
        self._account_number = account_number
        self._customer_id = customer_id
        # if not new, the value will already be normalised in the db.
        self._account_balance = (
            int((Decimal(account_balance) * 100).quantize(Decimal("1")))
            if is_new
            else account_balance
        )

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime | None) -> None:
        if self._created_at is not None:
            raise AttributeError("created_at cannot be set if not None")

        self._created_at = value

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def customer_id(self) -> UUID:
        return self._customer_id

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def account_type(self) -> str:
        return self._account_type

    @property
    def account_balance(self) -> NonNegativeInt:
        return int(self._account_balance)

    @validate_call
    def increase_balance(self, amount: NonNegativeFloat) -> None:
        self._account_balance += int((Decimal(amount) * 100).quantize(Decimal("1")))

    @validate_call
    def decrease_balance(self, amount: NonNegativeFloat) -> None:
        cents = int((Decimal(amount) * 100).quantize(Decimal("1")))
        if self._account_balance < cents:
            raise ValueError("insufficient funds for this transaction")

        self._account_balance -= cents

    @classmethod
    def from_record(cls, record: Any) -> Self:
        return cls(
            id=record.id,
            customer_id=record.customer_id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            account_type=record.account_type,
            account_number=record.account_number,
            account_balance=record.account_balance,
            is_new=False,
        )
