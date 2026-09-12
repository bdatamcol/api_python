import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Color(Base):
    __tablename__ = "colors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True,
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )

    hex_code: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
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
