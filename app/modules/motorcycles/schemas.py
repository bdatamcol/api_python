import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# BASE
# ============================================================

class MotorcycleBase(BaseModel):
    brand_id: uuid.UUID

    category_id: uuid.UUID | None = None

    name: str = Field(
        min_length=2,
        max_length=160,
        examples=["SWITCH 125"],
    )

    short_description: str | None = Field(
        default=None,
        examples=[
            "Motocicleta práctica para trabajo y uso diario"
        ],
    )

    description: str | None = Field(
        default=None,
        examples=[
            "La Victory Switch 125 es una motocicleta orientada "
            "al uso urbano y actividades de trabajo."
        ],
    )

    engine_cc: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=7,
        decimal_places=2,
        examples=[125],
    )


# ============================================================
# CREATE
# ============================================================

class MotorcycleCreate(MotorcycleBase):
    pass


# ============================================================
# UPDATE
# ============================================================

class MotorcycleUpdate(BaseModel):
    brand_id: uuid.UUID | None = None

    category_id: uuid.UUID | None = None

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    short_description: str | None = None

    description: str | None = None

    engine_cc: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=7,
        decimal_places=2,
    )

    active: bool | None = None


# ============================================================
# RESPONSE
# ============================================================

class MotorcycleResponse(MotorcycleBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    slug: str

    active: bool

    created_at: datetime

    updated_at: datetime
