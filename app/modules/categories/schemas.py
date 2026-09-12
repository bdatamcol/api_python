import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# BASE
# ============================================================

class CategoryBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Sport"],
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        examples=[
            "Motocicletas deportivas y street"
        ],
    )


# ============================================================
# CREATE
# ============================================================

class CategoryCreate(CategoryBase):
    pass


# ============================================================
# UPDATE
# ============================================================

class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    active: bool | None = None


# ============================================================
# RESPONSE
# ============================================================

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    slug: str
    active: bool
    created_at: datetime
    updated_at: datetime
