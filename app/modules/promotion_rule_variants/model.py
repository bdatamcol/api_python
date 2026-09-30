import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionRuleVariant(Base):
    __tablename__ = "promotion_rule_variants"

    # ============================================================
    # REGLA PROMOCIONAL
    #
    # Forma parte de la PK compuesta:
    #
    # promotion_rule_id + variant_id
    # ============================================================

    promotion_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_rules.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_variants_rule",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # VARIANTE EXACTA
    #
    # Ejemplo:
    #
    # SWITCH 125
    # 2026
    # Negro Mate
    # SKU 60005599
    #
    # Forma parte de la PK compuesta.
    # ============================================================

    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_variants.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_variants_variant",
        ),
        primary_key=True,
        nullable=False,
    )