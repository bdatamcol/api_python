import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
)


# ============================================================
# BASE
# ============================================================

class PromotionRuleVariantBase(BaseModel):
    promotion_rule_id: uuid.UUID

    variant_id: uuid.UUID


# ============================================================
# CREATE COMPLETO
# ============================================================

class PromotionRuleVariantCreate(
    PromotionRuleVariantBase
):
    pass


# ============================================================
# CREATE DESDE UNA REGLA
#
# Lo usaremos con:
#
# POST /promotion-rules/{rule_id}/variants
#
# promotion_rule_id viene en la URL.
# ============================================================

class PromotionRuleVariantCreateForRule(
    BaseModel
):
    variant_id: uuid.UUID


# ============================================================
# RESPONSE
# ============================================================

class PromotionRuleVariantResponse(
    PromotionRuleVariantBase
):
    model_config = ConfigDict(
        from_attributes=True
    )