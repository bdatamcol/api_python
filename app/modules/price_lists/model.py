import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PriceList(Base):
    __tablename__ = "price_lists"

    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(territory_id, store_id) <= 1",
            name="price_lists_location_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    territory_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "territories.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    store_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "stores.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
    )

    currency: Mapped[str] = mapped_column(
        CHAR(3),
        nullable=False,
        server_default=text("'COP'"),
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("100"),
    )

    source_system: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'MANUAL'"),
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
