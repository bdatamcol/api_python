import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MotorcycleAlias(Base):
    __tablename__ = "motorcycle_aliases"

    __table_args__ = (
        UniqueConstraint(
            "model_id",
            "normalized_alias",
            name="motorcycle_aliases_unique",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_models.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    alias: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    normalized_alias: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
