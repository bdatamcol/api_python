import uuid
from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# TIPOS DE DATO PERMITIDOS POR POSTGRESQL
# ============================================================

class SpecificationDataType(str, Enum):
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"


# ============================================================
# BASE
# ============================================================

class SpecificationDefinitionBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
        examples=["Potencia"],
    )

    unit: str | None = Field(
        default=None,
        max_length=50,
        examples=["HP"],
    )

    data_type: SpecificationDataType = Field(
        examples=[SpecificationDataType.NUMBER],
    )


# ============================================================
# CREATE
# ============================================================

class SpecificationDefinitionCreate(
    SpecificationDefinitionBase
):
    pass


# ============================================================
# UPDATE
# ============================================================

class SpecificationDefinitionUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    unit: str | None = Field(
        default=None,
        max_length=50,
    )

    data_type: SpecificationDataType | None = None


# ============================================================
# RESPONSE
# ============================================================

class SpecificationDefinitionResponse(
    SpecificationDefinitionBase
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    slug: str

    created_at: datetime