import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionRuleModel(Base):
    __tablename__ = "promotion_rule_models"

    # ============================================================
    # REGLA PROMOCIONAL
    #
    # Forma parte de la PK compuesta:
    #
    # promotion_rule_id + model_id
    # ============================================================

    promotion_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_rules.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_models_rule",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # MODELO DE MOTOCICLETA
    #
    # Ej:
    # SWITCH 125
    # NITRO 125
    # APACHE RTR 160
    # ============================================================

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_models.id",
            ondelete="CASCADE",
            name="fk_promotion_rule_models_model",
        ),
        primary_key=True,
        nullable=False,
    )