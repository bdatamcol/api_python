import uuid
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ============================================================
# BASE
# ============================================================

class PromotionRuleFundingBase(BaseModel):
    promotion_rule_id: uuid.UUID
    funding_source_id: uuid.UUID

    amount: int | None = Field(
        default=None,
        ge=0,
        examples=[500000],
    )

    percentage: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=7,
        decimal_places=3,
        examples=[Decimal("50.000")],
    )

    @model_validator(mode="after")
    def validate_funding_value(
        self,
    ):
        if (
            self.amount is None
            and self.percentage is None
        ):
            raise ValueError(
                "Debe especificar amount, percentage o ambos"
            )

        return self


# ============================================================
# CREATE COMPLETO
# ============================================================

class PromotionRuleFundingCreate(
    PromotionRuleFundingBase
):
    pass


# ============================================================
# CREATE DESDE UNA REGLA
#
# Lo usaremos con:
#
# POST /promotion-rules/{rule_id}/funding
#
# promotion_rule_id viene en la URL.
# ============================================================

class PromotionRuleFundingCreateForRule(
    BaseModel
):
    funding_source_id: uuid.UUID

    amount: int | None = Field(
        default=None,
        ge=0,
        examples=[500000],
    )

    percentage: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=7,
        decimal_places=3,
        examples=[Decimal("50.000")],
    )

    @model_validator(mode="after")
    def validate_funding_value(
        self,
    ):
        if (
            self.amount is None
            and self.percentage is None
        ):
            raise ValueError(
                "Debe especificar amount, percentage o ambos"
            )

        return self


# ============================================================
# UPDATE
#
# Aquí NO validamos que al menos uno tenga valor porque en un
# PATCH necesitamos combinar estos datos con los valores que
# ya existen en PostgreSQL.
#
# Esa validación la hará el service.
# ============================================================

class PromotionRuleFundingUpdate(
    BaseModel
):
    amount: int | None = Field(
        default=None,
        ge=0,
        examples=[500000],
    )

    percentage: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=7,
        decimal_places=3,
        examples=[Decimal("50.000")],
    )


# ============================================================
# RESPONSE
# ============================================================

class PromotionRuleFundingResponse(
    PromotionRuleFundingBase
):
    model_config = ConfigDict(
        from_attributes=True
    )
