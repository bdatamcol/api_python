import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    FetchedValue,
    ForeignKey,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import DATERANGE, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VariantPrice(Base):
    __tablename__ = "variant_prices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ============================================================
    # LISTA DE PRECIOS
    #
    # Ej:
    # Precio Comercial Cúcuta
    # ============================================================

    price_list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "price_lists.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # ============================================================
    # VARIANTE
    #
    # Ej:
    # SWITCH 125 - 2026 - NEGRO - SKU 60005599
    # ============================================================

    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_variants.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # ============================================================
    # PRECIO
    #
    # Guardamos dinero como entero.
    #
    # $7.449.000 COP
    #
    # ->
    #
    # 7449000
    # ============================================================

    amount: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # ============================================================
    # VIGENCIA
    # ============================================================

    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    valid_until: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # ============================================================
    # RANGO GENERADO POR POSTGRESQL
    #
    # Esta columna ya existe en la BD.
    # La base de datos la calcula automáticamente.
    #
    # NO la vamos a enviar al crear o actualizar precios.
    # ============================================================

    validity: Mapped[object] = mapped_column(
        DATERANGE,
        nullable=False,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue(),
    )

    # ============================================================
    # REFERENCIA DEL ORIGEN
    #
    # Ej:
    # ERP-LISTA-29
    # CARGA-SEPTIEMBRE-2026
    # MANUAL
    # ============================================================

    source_reference: Mapped[str | None] = mapped_column(
        String(255),
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
