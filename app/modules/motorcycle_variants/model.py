import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MotorcycleVariant(Base):
    __tablename__ = "motorcycle_variants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ============================================================
    # MODELO
    #
    # Ej:
    # SWITCH 125
    # ============================================================

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_models.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # ============================================================
    # COLOR
    # ============================================================

    color_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "colors.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ============================================================
    # SKU
    #
    # Puede venir del ERP o ser definido manualmente.
    # Ej:
    # 60005599
    # ============================================================

    sku: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # ============================================================
    # AÑO MODELO
    #
    # Ej:
    # 2026
    # ============================================================

    model_year: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    # ============================================================
    # NOMBRE COMERCIAL COMPLETO
    #
    # Ej:
    # VICTORY SWITCH 125 NEGRO MATE CALCA DORADA 2026
    # ============================================================

    commercial_name: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    # ============================================================
    # SISTEMA ORIGEN
    #
    # MANUAL
    # ERP
    # IMPORT
    # API
    # ============================================================

    source_system: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'MANUAL'"),
    )

    # ============================================================
    # CODIGO EXTERNO
    #
    # Por ejemplo el código del producto en el ERP.
    # ============================================================

    external_code: Mapped[str | None] = mapped_column(
        String(100),
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
