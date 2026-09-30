import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
)


# ============================================================
# BASE
# ============================================================

class PromotionCampaignBrandBase(BaseModel):
    campaign_id: uuid.UUID

    brand_id: uuid.UUID


# ============================================================
# CREATE
# ============================================================

class PromotionCampaignBrandCreate(
    PromotionCampaignBrandBase
):
    pass


# ============================================================
# CREATE DESDE UNA CAMPAÑA
#
# Lo usaremos con:
#
# POST /promotion-campaigns/{campaign_id}/brands
#
# Así campaign_id viene en la URL.
# ============================================================

class PromotionCampaignBrandCreateForCampaign(
    BaseModel
):
    brand_id: uuid.UUID


# ============================================================
# RESPONSE
# ============================================================

class PromotionCampaignBrandResponse(
    PromotionCampaignBrandBase
):
    model_config = ConfigDict(
        from_attributes=True
    )