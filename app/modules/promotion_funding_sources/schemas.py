import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# BASE
# ============================================================

class PromotionFundingSourceBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
        examples=["UMA"],
    )

    code: str = Field(
        min_length=1,
        max_length=50,
        examples=["UMA"],
    )


# ============================================================
# CREATE
# ============================================================

class PromotionFundingSourceCreate(
    PromotionFundingSourceBase
):
    pass


# ============================================================
# UPDATE
# ============================================================

class PromotionFundingSourceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    active: bool | None = None


# ============================================================
# RESPONSE
# ============================================================

class PromotionFundingSourceResponse(
    PromotionFundingSourceBase
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    active: bool

    created_at: datetime