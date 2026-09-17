import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# BASE
# ============================================================

class PromotionRuleYearBase(BaseModel):
    promotion_rule_id: uuid.UUID

    model_year: int = Field(
        ge=1990,
        le=2100,
        examples=[2026],
    )


# ============================================================
# CREATE COMPLETO
# ============================================================

class PromotionRuleYearCreate(
    PromotionRuleYearBase
):
    pass


# ============================================================
# CREATE DESDE UNA REGLA
#
# Lo usaremos con:
#
# POST /promotion-rules/{rule_id}/years
#
# promotion_rule_id viene en la URL.
# ============================================================

class PromotionRuleYearCreateForRule(BaseModel):
    model_year: int = Field(
        ge=1990,
        le=2100,
        examples=[2026],
    )


# ============================================================
# RESPONSE
# ============================================================

class PromotionRuleYearResponse(
    PromotionRuleYearBase
):
    model_config = ConfigDict(
        from_attributes=True
    )