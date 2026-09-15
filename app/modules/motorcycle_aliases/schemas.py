import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# BASE
# ============================================================

class MotorcycleAliasBase(BaseModel):
    alias: str = Field(
        min_length=1,
        max_length=200,
        examples=["victory switch 125"],
    )


# ============================================================
# CREATE
# ============================================================

class MotorcycleAliasCreate(MotorcycleAliasBase):
    model_id: uuid.UUID


# ============================================================
# CREATE DESDE UNA MOTO
#
# Lo usaremos después en un endpoint tipo:
# POST /motorcycles/{motorcycle_id}/aliases
#
# Así el frontend no necesita mandar model_id en el body.
# ============================================================

class MotorcycleAliasCreateForModel(MotorcycleAliasBase):
    pass


# ============================================================
# UPDATE
# ============================================================

class MotorcycleAliasUpdate(BaseModel):
    alias: str = Field(
        min_length=1,
        max_length=200,
    )


# ============================================================
# RESPONSE
# ============================================================

class MotorcycleAliasResponse(MotorcycleAliasBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    model_id: uuid.UUID
    normalized_alias: str
    created_at: datetime
