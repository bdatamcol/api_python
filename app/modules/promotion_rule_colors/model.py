import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionRuleColor(Base):
    __tablename__ = "promotion_rule_colors"

    # ============================================================
    # REGLA PROMOCIONAL
    #
    # Forma parte de la PK compuesta:
    #
    # promotion_rule_id + color_id
    # ============================================================

    promotion_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_rules.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_colors_rule",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # COLOR
    #
    # Ej:
    # Negro Mate
    # Rojo
    # Gris
    #
    # Forma parte de la PK compuesta.
    # ============================================================

    color_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "colors.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_colors_color",
        ),
        primary_key=True,
        nullable=False,
    )