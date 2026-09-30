import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ============================================================
# ESTADOS PERMITIDOS POR POSTGRESQL
# ============================================================

class PromotionCampaignStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


# ============================================================
# BASE
# ============================================================

class PromotionCampaignBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=220,
        examples=["Bonos Septiembre Victory"],
    )

    description: str | None = Field(
        default=None,
        examples=[
            "Campaña promocional para modelos seleccionados durante septiembre."
        ],
    )

    start_date: date = Field(
        examples=["2026-09-01"],
    )

    end_date: date = Field(
        examples=["2026-09-30"],
    )

    status: PromotionCampaignStatus = (
        PromotionCampaignStatus.DRAFT
    )

    stackable: bool = False

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial"
            )

        return self


# ============================================================
# CREATE
# ============================================================

class PromotionCampaignCreate(
    PromotionCampaignBase
):
    pass


# ============================================================
# UPDATE
# ============================================================

class PromotionCampaignUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=220,
    )

    description: str | None = None

    start_date: date | None = None

    end_date: date | None = None

    status: PromotionCampaignStatus | None = None

    stackable: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        # Si llegan ambas fechas podemos validarlas aquí.
        # Si solamente llega una, el service comparará
        # contra el valor actual de PostgreSQL.
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial"
            )

        return self


# ============================================================
# RESPONSE
# ============================================================

class PromotionCampaignResponse(
    PromotionCampaignBase
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    created_at: datetime

    updated_at: datetime