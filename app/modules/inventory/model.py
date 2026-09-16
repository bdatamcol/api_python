import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "variant_id",
            "store_id",
            name="inventory_variant_store_unique",
        ),
        CheckConstraint(
            "quantity >= 0",
            name="inventory_quantity_nonnegative",
        ),
        CheckConstraint(
            "reserved_quantity >= 0",
            name="inventory_reserved_quantity_nonnegative",
        ),
        CheckConstraint(
            "reserved_quantity <= quantity",
            name="inventory_reserved_quantity_lte_quantity",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_variants.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "stores.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    reserved_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    available_quantity: Mapped[int] = mapped_column(
        Integer,
        Computed(
            "quantity - reserved_quantity",
            persisted=True,
        ),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
