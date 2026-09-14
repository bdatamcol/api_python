import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StoreBase(BaseModel):
    territory_id: uuid.UUID

    name: str = Field(
        min_length=2,
        max_length=180,
        examples=["Japolandia Avenida Quinta"],
    )

    code: str = Field(
        min_length=2,
        max_length=80,
        examples=["JAPO-AV5"],
    )

    address: str | None = Field(
        default=None,
        examples=["Avenida Quinta, Cúcuta"],
    )


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    territory_id: uuid.UUID | None = None

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=180,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=80,
    )

    address: str | None = None

    active: bool | None = None


class StoreResponse(StoreBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    active: bool
    created_at: datetime
    updated_at: datetime
