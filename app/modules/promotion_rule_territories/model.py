import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionRuleTerritory(Base):
    __tablename__ = "promotion_rule_territories"

    # ============================================================
    # REGLA PROMOCIONAL
    #
    # Forma parte de la PK compuesta:
    #
    # promotion_rule_id + territory_id
    # ============================================================

    promotion_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_rules.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_territories_rule",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # TERRITORIO
    #
    # Puede representar, según nuestra estructura:
    #
    # COUNTRY
    # DEPARTMENT
    # CITY
    # ZONE
    #
    # También forma parte de la PK compuesta.
    # ============================================================

    territory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "territories.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_territories_territory",
        ),
        primary_key=True,
        nullable=False,
    )
