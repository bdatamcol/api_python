import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionCampaignBrand(Base):
    __tablename__ = "promotion_campaign_brands"

    # ============================================================
    # CAMPAÑA
    #
    # Forma parte de la PK compuesta:
    #
    # campaign_id + brand_id
    # ============================================================

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_campaigns.id",
            ondelete="CASCADE",
            name="fk_promotion_campaign_brands_campaign",
        ),
        primary_key=True,
        nullable=False,
    )

    # ============================================================
    # MARCA
    #
    # Forma parte de la PK compuesta.
    #
    # Ej:
    # TVS
    # VICTORY
    # BAJAJ
    # ============================================================

    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "brands.id",
            ondelete="CASCADE",
            name="fk_promotion_campaign_brands_brand",
        ),
        primary_key=True,
        nullable=False,
    )