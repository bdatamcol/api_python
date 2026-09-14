import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# TIPOS DE TERRITORIO
# ============================================================

class TerritoryType(str, Enum):
    COUNTRY = "COUNTRY"
    DEPARTMENT = "DEPARTMENT"
    CITY = "CITY"
    ZONE = "ZONE"


# ============================================================
# BASE
# ============================================================

class TerritoryBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
        examples=["Cúcuta"],
    )

    type: TerritoryType

    parent_id: uuid.UUID | None = Field(
        default=None,
        description="Territorio padre. Ej: Cúcuta pertenece a Norte de Santander.",
    )

    code: str | None = Field(
        default=None,
        max_length=50,
        examples=["CO-NSA-CUC"],
    )


# ============================================================
# CREATE
# ============================================================

class TerritoryCreate(TerritoryBase):
    pass


# ============================================================
# UPDATE
# ============================================================

class TerritoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    type: TerritoryType | None = None

    parent_id: uuid.UUID | None = None

    code: str | None = Field(
        default=None,
        max_length=50,
    )

    active: bool | None = None


# ============================================================
# RESPONSE
# ============================================================

class TerritoryResponse(TerritoryBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    active: bool
    created_at: datetime
    updated_at: datetime
