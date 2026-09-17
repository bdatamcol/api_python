import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
)


# ============================================================
# BASE
# ============================================================

class PromotionRuleModelBase(BaseModel):
    promotion_rule_id: uuid.UUID

    model_id: uuid.UUID


# ============================================================
# CREATE
# ============================================================

class PromotionRuleModelCreate(
    PromotionRuleModelBase
):
    pass


# ============================================================
# CREATE DESDE UNA REGLA
#
# Lo usaremos con:
#
# POST /promotion-rules/{rule_id}/models
#
# promotion_rule_id viene en la URL.
# ============================================================

class PromotionRuleModelCreateForRule(
    BaseModel
):
    model_id: uuid.UUID


# ============================================================
# RESPONSE
# ============================================================

class PromotionRuleModelResponse(
    PromotionRuleModelBase
):
    model_config = ConfigDict(
        from_attributes=True
    )