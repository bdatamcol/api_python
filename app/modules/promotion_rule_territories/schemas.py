import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
)


# ============================================================
# BASE
# ============================================================

class PromotionRuleTerritoryBase(BaseModel):
    promotion_rule_id: uuid.UUID
    territory_id: uuid.UUID


# ============================================================
# CREATE COMPLETO
# ============================================================

class PromotionRuleTerritoryCreate(
    PromotionRuleTerritoryBase
):
    pass


# ============================================================
# CREATE DESDE UNA REGLA
#
# Lo usaremos con:
#
# POST /promotion-rules/{rule_id}/territories
#
# promotion_rule_id viene en la URL.
# ============================================================

class PromotionRuleTerritoryCreateForRule(
    BaseModel
):
    territory_id: uuid.UUID


# ============================================================
# RESPONSE
# ============================================================

class PromotionRuleTerritoryResponse(
    PromotionRuleTerritoryBase
):
    model_config = ConfigDict(
        from_attributes=True
    )
