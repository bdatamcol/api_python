import uuid
from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# SISTEMA DE ORIGEN
# ============================================================

class VariantSourceSystem(str, Enum):
    MANUAL = "MANUAL"
    ERP = "ERP"
    IMPORT = "IMPORT"
    API = "API"


# ============================================================
# BASE
# ============================================================

class MotorcycleVariantBase(BaseModel):
    model_id: uuid.UUID

    color_id: uuid.UUID | None = None

    sku: str | None = Field(
        default=None,
        max_length=100,
        examples=["60005599"],
    )

    model_year: int | None = Field(
        default=None,
        ge=1990,
        le=2100,
        examples=[2026],
    )

    commercial_name: str | None = Field(
        default=None,
        max_length=250,
        examples=[
            "VICTORY SWITCH 125 NEGRO MATE CALCA DORADA 2026"
        ],
    )

    source_system: VariantSourceSystem = (
        VariantSourceSystem.MANUAL
    )

    external_code: str | None = Field(
        default=None,
        max_length=100,
        examples=["60005599"],
    )


# ============================================================
# CREATE
# ============================================================

class MotorcycleVariantCreate(
    MotorcycleVariantBase
):
    pass


# ============================================================
# CREATE DESDE UNA MOTOCICLETA
#
# Para un endpoint posterior:
#
# POST /motorcycles/{motorcycle_id}/variants
#
# El frontend no tendrá que enviar model_id.
# ============================================================

class MotorcycleVariantCreateForModel(
    BaseModel
):
    color_id: uuid.UUID | None = None

    sku: str | None = Field(
        default=None,
        max_length=100,
    )

    model_year: int | None = Field(
        default=None,
        ge=1990,
        le=2100,
    )

    commercial_name: str | None = Field(
        default=None,
        max_length=250,
    )

    source_system: VariantSourceSystem = (
        VariantSourceSystem.MANUAL
    )

    external_code: str | None = Field(
        default=None,
        max_length=100,
    )


# ============================================================
# UPDATE
# ============================================================

class MotorcycleVariantUpdate(
    BaseModel
):
    color_id: uuid.UUID | None = None

    sku: str | None = Field(
        default=None,
        max_length=100,
    )

    model_year: int | None = Field(
        default=None,
        ge=1990,
        le=2100,
    )

    commercial_name: str | None = Field(
        default=None,
        max_length=250,
    )

    source_system: VariantSourceSystem | None = None

    external_code: str | None = Field(
        default=None,
        max_length=100,
    )

    active: bool | None = None


# ============================================================
# RESPONSE
# ============================================================

class MotorcycleVariantResponse(
    MotorcycleVariantBase
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    active: bool

    created_at: datetime

    updated_at: datetime
