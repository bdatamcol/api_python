import uuid
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionRuleFunding(Base):
    __tablename__ = "promotion_rule_funding"

    __table_args__ = (
        # ========================================================
        # DEBE EXISTIR AL MENOS UN VALOR
        #
        # amount o percentage
        # ========================================================
        CheckConstraint(
            """
            amount IS NOT NULL
            OR percentage IS NOT NULL
            """,
            name="promotion_rule_funding_value_check",
        ),

        # ========================================================
        # MONTO NO NEGATIVO
        # ========================================================
        CheckConstraint(
            """
            amount IS NULL
            OR amount >= 0
            """,
            name="promotion_rule_funding_amount_check",
        ),

        # ========================================================
        # PORCENTAJE ENTRE 0 Y 100
        # ========================================================
        CheckConstraint(
            """
            percentage IS NULL
            OR (
                percentage >= 0
                AND percentage <= 100
            )
            """,
            name="promotion_rule_funding_percentage_check",
        ),
    )

    # ============================================================
    # REGLA PROMOCIONAL
    #
    # Forma parte de la PK compuesta:
    #
    # promotion_rule_id + funding_source_id
    # ============================================================

    promotion_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_rules.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_funding_rule",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # FUENTE DE FINANCIACION / APORTE
    #
    # Ej:
    # UMA
    # PDV
    # Fabricante
    # Concesionario
    # ============================================================

    funding_source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_funding_sources.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_funding_source",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # MONTO FIJO APORTADO
    #
    # PostgreSQL:
    # BIGINT
    #
    # Ej:
    # 500000
    # ============================================================

    amount: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # ============================================================
    # PORCENTAJE APORTADO
    #
    # PostgreSQL:
    # NUMERIC(7,3)
    #
    # Ej:
    # 10.000
    # 50.000
    # ============================================================

    percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(
            precision=7,
            scale=3,
        ),
        nullable=True,
    )
