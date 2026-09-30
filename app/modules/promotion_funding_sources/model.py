import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionFundingSource(Base):
    __tablename__ = "promotion_funding_sources"

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="promotion_funding_sources_name_unique",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ============================================================
    # NOMBRE
    #
    # Ej:
    # UMA
    # PDV
    # Fabricante
    # Concesionario
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    # ============================================================
    # CODIGO
    #
    # Ej:
    # UMA
    # PDV
    # MANUFACTURER
    # DEALER
    #
    # En PostgreSQL es UNIQUE.
    # ============================================================

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
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