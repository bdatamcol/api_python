import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SpecificationDefinition(Base):
    __tablename__ = "specification_definitions"

    __table_args__ = (
        CheckConstraint(
            "data_type IN ('TEXT', 'NUMBER', 'BOOLEAN', 'JSON')",
            name="specification_definitions_type_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(170),
        nullable=False,
        unique=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    data_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
