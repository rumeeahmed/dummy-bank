import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from repository.db_customer import Base


class DBAddress(Base):
    __tablename__ = "addresses"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    building_name: Mapped[str] = mapped_column(String, nullable=True)
    building_number: Mapped[str] = mapped_column(String, nullable=False)
    street: Mapped[str] = mapped_column(String, nullable=False)
    town: Mapped[str] = mapped_column(String, nullable=False)
    post_code: Mapped[str] = mapped_column(String, nullable=False)
    county: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[str] = mapped_column(String, nullable=True)
    longitude: Mapped[str] = mapped_column(String, nullable=True)
    customer = relationship("DBCustomer", backref="addresses")
