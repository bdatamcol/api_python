import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# BASE
# Campos compartidos
# ============================================================

class BrandBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["VICTORY"],
    )


# ============================================================
# CREATE
# Equivalente a CreateBrandDto
# ============================================================

class BrandCreate(BrandBase):
    pass


# ============================================================
# UPDATE
# Equivalente a UpdateBrandDto / PartialType
# Todos los campos son opcionales
# ============================================================

class BrandUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    active: bool | None = None


# ============================================================
# RESPONSE
# Lo que devuelve nuestra API
# ============================================================

class BrandResponse(BrandBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    slug: str
    active: bool
    created_at: datetime
    updated_at: datetime
