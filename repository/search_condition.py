from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr


class SearchCondition(BaseModel):
    id: UUID | None = None
    email: EmailStr | None = None
    customer_id: UUID | None = None

    def as_filter_by_kwargs(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)
