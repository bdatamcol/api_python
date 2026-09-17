import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ============================================================
# TIPOS DE BENEFICIO
# ============================================================

class PromotionBenefitType(str, Enum):
    FIXED_DISCOUNT = "FIXED_DISCOUNT"
    PERCENTAGE_DISCOUNT = "PERCENTAGE_DISCOUNT"
    BONUS = "BONUS"
    CASHBACK = "CASHBACK"
    GIFT = "GIFT"


# ============================================================
# CAMPOS DEL BENEFICIO
# ============================================================

class PromotionRuleFields(BaseModel):
    name: str | None = Field(
        default=None,
        max_length=220,
        examples=["Bono Victory Switch 125"],
    )

    benefit_type: PromotionBenefitType

    benefit_amount: int | None = Field(
        default=None,
        ge=0,
        examples=[500000],
    )

    benefit_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=7,
        decimal_places=3,
        examples=[10],
    )

    gift_description: str | None = Field(
        default=None,
        examples=["Casco certificado"],
    )

    terms: str | None = Field(
        default=None,
        examples=[
            "Aplica únicamente durante la vigencia de la campaña."
        ],
    )

    priority: int = 100

    active: bool = True

    # ========================================================
    # VALIDAR BENEFICIO
    # ========================================================

    @model_validator(mode="after")
    def validate_benefit(self):
        benefit_type = self.benefit_type

        # --------------------------------------------------------
        # DESCUENTO FIJO / BONO / CASHBACK
        # --------------------------------------------------------

        if benefit_type in {
            PromotionBenefitType.FIXED_DISCOUNT,
            PromotionBenefitType.BONUS,
            PromotionBenefitType.CASHBACK,
        }:
            if self.benefit_amount is None:
                raise ValueError(
                    f"{benefit_type.value} requiere benefit_amount"
                )

            if self.benefit_percentage is not None:
                raise ValueError(
                    f"{benefit_type.value} no utiliza benefit_percentage"
                )

            if self.gift_description is not None:
                raise ValueError(
                    f"{benefit_type.value} no utiliza gift_description"
                )

        # --------------------------------------------------------
        # DESCUENTO PORCENTUAL
        # --------------------------------------------------------

        elif (
            benefit_type
            == PromotionBenefitType.PERCENTAGE_DISCOUNT
        ):
            if self.benefit_percentage is None:
                raise ValueError(
                    "PERCENTAGE_DISCOUNT requiere benefit_percentage"
                )

            if self.benefit_amount is not None:
                raise ValueError(
                    "PERCENTAGE_DISCOUNT no utiliza benefit_amount"
                )

            if self.gift_description is not None:
                raise ValueError(
                    "PERCENTAGE_DISCOUNT no utiliza gift_description"
                )

        # --------------------------------------------------------
        # OBSEQUIO
        # --------------------------------------------------------

        elif benefit_type == PromotionBenefitType.GIFT:
            if (
                self.gift_description is None
                or not self.gift_description.strip()
            ):
                raise ValueError(
                    "GIFT requiere gift_description"
                )

            if self.benefit_amount is not None:
                raise ValueError(
                    "GIFT no utiliza benefit_amount"
                )

            if self.benefit_percentage is not None:
                raise ValueError(
                    "GIFT no utiliza benefit_percentage"
                )

        return self


# ============================================================
# CREATE COMPLETO
# ============================================================

class PromotionRuleCreate(
    PromotionRuleFields
):
    campaign_id: uuid.UUID


# ============================================================
# CREATE DESDE UNA CAMPAÑA
#
# POST /promotion-campaigns/{campaign_id}/rules
#
# campaign_id vendrá en la URL.
# ============================================================

class PromotionRuleCreateForCampaign(
    PromotionRuleFields
):
    pass


# ============================================================
# UPDATE
#
# Aquí NO podemos hacer la misma validación completa,
# porque un PATCH puede enviar solamente:
#
# {
#     "priority": 50
# }
#
# El service validará el estado FINAL del registro.
# ============================================================

class PromotionRuleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        max_length=220,
    )

    benefit_type: PromotionBenefitType | None = None

    benefit_amount: int | None = Field(
        default=None,
        ge=0,
    )

    benefit_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=7,
        decimal_places=3,
    )

    gift_description: str | None = None

    terms: str | None = None

    priority: int | None = None

    active: bool | None = None


# ============================================================
# RESPONSE
# ============================================================

class PromotionRuleResponse(
    PromotionRuleFields
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    campaign_id: uuid.UUID

    created_at: datetime

    updated_at: datetime