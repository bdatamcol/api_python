import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ============================================================
# BASE
# ============================================================

class PriceListBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=160,
        examples=["Precio Comercial Cúcuta"],
    )

    code: str = Field(
        min_length=2,
        max_length=80,
        examples=["CUCUTA-RETAIL"],
    )

    territory_id: uuid.UUID | None = None

    store_id: uuid.UUID | None = None

    currency: str = Field(
        default="COP",
        min_length=3,
        max_length=3,
        examples=["COP"],
    )

    priority: int = Field(
        default=100,
        ge=0,
        examples=[10],
    )

    source_system: str = Field(
        default="MANUAL",
        min_length=2,
        max_length=50,
        examples=["MANUAL"],
    )

    # ========================================================
    # VALIDAR MONEDA
    # ========================================================

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.strip().upper()

        if len(value) != 3 or not value.isalpha():
            raise ValueError(
                "La moneda debe tener exactamente 3 letras, por ejemplo COP"
            )

        return value

    # ========================================================
    # VALIDAR UBICACION
    #
    # Puede tener:
    # territory_id
    # O
    # store_id
    # O ninguno
    #
    # Pero nunca ambos.
    # ========================================================

    @model_validator(mode="after")
    def validate_location(self):

        if (
            self.territory_id is not None
            and self.store_id is not None
        ):
            raise ValueError(
                "Una lista de precios no puede pertenecer a un territorio y a una sede al mismo tiempo"
            )

        return self


# ============================================================
# CREATE
# ============================================================

class PriceListCreate(PriceListBase):
    pass


# ============================================================
# UPDATE
# ============================================================

class PriceListUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=160,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=80,
    )

    territory_id: uuid.UUID | None = None

    store_id: uuid.UUID | None = None

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    priority: int | None = Field(
        default=None,
        ge=0,
    )

    source_system: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    active: bool | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip().upper()

        if len(value) != 3 or not value.isalpha():
            raise ValueError(
                "La moneda debe tener exactamente 3 letras, por ejemplo COP"
            )

        return value

    @model_validator(mode="after")
    def validate_location(self):

        if (
            self.territory_id is not None
            and self.store_id is not None
        ):
            raise ValueError(
                "No puedes asignar territorio y sede al mismo tiempo"
            )

        return self


# ============================================================
# RESPONSE
# ============================================================

class PriceListResponse(PriceListBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    active: bool
    created_at: datetime
    updated_at: datetime
