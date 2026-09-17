import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionCampaign(Base):
    __tablename__ = "promotion_campaigns"

    __table_args__ = (
        CheckConstraint(
            "end_date >= start_date",
            name="promotion_campaigns_dates_check",
        ),
        CheckConstraint(
            """
            status IN (
                'DRAFT',
                'ACTIVE',
                'EXPIRED',
                'CANCELLED'
            )
            """,
            name="promotion_campaigns_status_check",
        ),
    )

    # ============================================================
    # ID
    # ============================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ============================================================
    # NOMBRE
    #
    # Ej:
    # Bonos Septiembre TVS
    # Descuentos especiales Victory 2026
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(220),
        nullable=False,
    )

    # ============================================================
    # DESCRIPCION
    # ============================================================

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # VIGENCIA
    # ============================================================

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # ============================================================
    # ESTADO
    #
    # DRAFT
    # ACTIVE
    # EXPIRED
    # CANCELLED
    # ============================================================

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'DRAFT'"),
    )

    # ============================================================
    # ACUMULABLE
    #
    # false:
    # La promoción no puede combinarse con otras.
    #
    # true:
    # Puede combinarse con otras promociones.
    # ============================================================

    stackable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    # ============================================================
    # FECHAS
    # ============================================================

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