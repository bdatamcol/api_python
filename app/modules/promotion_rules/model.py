import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionRule(Base):
    __tablename__ = "promotion_rules"

    __table_args__ = (
        # ========================================================
        # TIPO DE BENEFICIO
        # ========================================================
        CheckConstraint(
            """
            benefit_type IN (
                'FIXED_DISCOUNT',
                'PERCENTAGE_DISCOUNT',
                'BONUS',
                'CASHBACK',
                'GIFT'
            )
            """,
            name="promotion_rules_type_check",
        ),

        # ========================================================
        # MONTO NO NEGATIVO
        # ========================================================
        CheckConstraint(
            """
            benefit_amount IS NULL
            OR benefit_amount >= 0
            """,
            name="promotion_rules_amount_check",
        ),

        # ========================================================
        # PORCENTAJE ENTRE 0 Y 100
        # ========================================================
        CheckConstraint(
            """
            benefit_percentage IS NULL
            OR (
                benefit_percentage >= 0
                AND benefit_percentage <= 100
            )
            """,
            name="promotion_rules_percentage_check",
        ),

        # ========================================================
        # VALOR OBLIGATORIO SEGÚN TIPO
        #
        # FIXED_DISCOUNT / BONUS / CASHBACK
        #     -> benefit_amount
        #
        # PERCENTAGE_DISCOUNT
        #     -> benefit_percentage
        #
        # GIFT
        #     -> gift_description
        # ========================================================
        CheckConstraint(
            """
            (
                benefit_type IN (
                    'FIXED_DISCOUNT',
                    'BONUS',
                    'CASHBACK'
                )
                AND benefit_amount IS NOT NULL
            )
            OR
            (
                benefit_type = 'PERCENTAGE_DISCOUNT'
                AND benefit_percentage IS NOT NULL
            )
            OR
            (
                benefit_type = 'GIFT'
                AND gift_description IS NOT NULL
            )
            """,
            name="promotion_rules_value_check",
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
    # CAMPAÑA
    # ============================================================

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_campaigns.id",
            ondelete="CASCADE",
            name="fk_promotion_rules_campaign",
        ),
        nullable=False,
    )

    # ============================================================
    # NOMBRE DE LA REGLA
    #
    # Ej:
    # Bono Apache RTR 310
    # Descuento Raider 125
    # Casco gratis Ntorq
    # ============================================================

    name: Mapped[str | None] = mapped_column(
        String(220),
        nullable=True,
    )

    # ============================================================
    # TIPO DE BENEFICIO
    #
    # FIXED_DISCOUNT
    # PERCENTAGE_DISCOUNT
    # BONUS
    # CASHBACK
    # GIFT
    # ============================================================

    benefit_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # ============================================================
    # MONTO
    #
    # Para:
    # FIXED_DISCOUNT
    # BONUS
    # CASHBACK
    #
    # Ej:
    # $1.000.000 -> 1000000
    # ============================================================

    benefit_amount: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # ============================================================
    # PORCENTAJE
    #
    # Para:
    # PERCENTAGE_DISCOUNT
    #
    # Ej:
    # 10.5 %
    # ============================================================

    benefit_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(
            precision=7,
            scale=3,
        ),
        nullable=True,
    )

    # ============================================================
    # DESCRIPCIÓN DEL OBSEQUIO
    #
    # Para:
    # GIFT
    #
    # Ej:
    # Casco certificado
    # SOAT gratis
    # ============================================================

    gift_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # TÉRMINOS / CONDICIONES
    # ============================================================

    terms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # PRIORIDAD
    #
    # Menor número puede representar mayor prioridad
    # cuando posteriormente evaluemos varias reglas.
    # ============================================================

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("100"),
    )

    # ============================================================
    # ACTIVA
    # ============================================================

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
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