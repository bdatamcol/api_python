import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
)


# ============================================================
# BASE
# ============================================================

class PromotionRuleColorBase(BaseModel):
    promotion_rule_id: uuid.UUID

    color_id: uuid.UUID


# ============================================================
# CREATE COMPLETO
# ============================================================

class PromotionRuleColorCreate(
    PromotionRuleColorBase
):
    pass


# ============================================================
# CREATE DESDE UNA REGLA
#
# Lo usaremos con:
#
# POST /promotion-rules/{rule_id}/colors
#
# promotion_rule_id viene en la URL.
# ============================================================

class PromotionRuleColorCreateForRule(
    BaseModel
):
    color_id: uuid.UUID


# ============================================================
# RESPONSE
# ============================================================

class PromotionRuleColorResponse(
    PromotionRuleColorBase
):
    model_config = ConfigDict(
        from_attributes=True
    )