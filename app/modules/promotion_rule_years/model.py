import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionRuleYear(Base):
    __tablename__ = "promotion_rule_years"

    __table_args__ = (
        CheckConstraint(
            "model_year BETWEEN 1990 AND 2100",
            name="promotion_rule_years_check",
        ),
    )

    # ============================================================
    # REGLA PROMOCIONAL
    #
    # Forma parte de la PK compuesta:
    #
    # promotion_rule_id + model_year
    # ============================================================

    promotion_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_rules.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_years_rule",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # AÑO MODELO
    #
    # PostgreSQL:
    # SMALLINT
    #
    # Valores permitidos:
    # 1990 - 2100
    #
    # Ej:
    # 2025
    # 2026
    # ============================================================

    model_year: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        nullable=False,
    )