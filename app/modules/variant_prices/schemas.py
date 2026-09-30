import uuid
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ============================================================
# BASE
# ============================================================

class VariantPriceBase(BaseModel):
    price_list_id: uuid.UUID

    variant_id: uuid.UUID

    amount: int = Field(
        gt=0,
        examples=[7449000],
    )

    valid_from: date = Field(
        examples=["2026-09-01"],
    )

    valid_until: date | None = Field(
        default=None,
        examples=["2026-12-31"],
    )

    source_reference: str | None = Field(
        default=None,
        max_length=255,
        examples=["ERP-LISTA-29"],
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.valid_until is not None
            and self.valid_until < self.valid_from
        ):
            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial"
            )

        return self


# ============================================================
# CREATE
# ============================================================

class VariantPriceCreate(
    VariantPriceBase
):
    pass


# ============================================================
# CREATE DESDE UNA VARIANTE
#
# Lo usaremos con:
#
# POST /motorcycle-variants/{variant_id}/prices
#
# El frontend no tendrá que enviar variant_id.
# ============================================================

class VariantPriceCreateForVariant(
    BaseModel
):
    price_list_id: uuid.UUID

    amount: int = Field(
        gt=0,
        examples=[7449000],
    )

    valid_from: date = Field(
        examples=["2026-09-01"],
    )

    valid_until: date | None = None

    source_reference: str | None = Field(
        default=None,
        max_length=255,
        examples=["ERP-LISTA-29"],
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.valid_until is not None
            and self.valid_until < self.valid_from
        ):
            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial"
            )

        return self


# ============================================================
# UPDATE
# ============================================================

class VariantPriceUpdate(
    BaseModel
):
    amount: int | None = Field(
        default=None,
        gt=0,
    )

    valid_from: date | None = None

    valid_until: date | None = None

    source_reference: str | None = Field(
        default=None,
        max_length=255,
    )

    active: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        # Si en el PATCH llegan ambas fechas,
        # podemos validarlas directamente.
        #
        # Si llega solamente una, el service validará
        # el resultado final contra los datos actuales.
        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_until < self.valid_from
        ):
            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial"
            )

        return self


# ============================================================
# RESPONSE
# ============================================================

class VariantPriceResponse(
    VariantPriceBase
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    active: bool

    created_at: datetime

    updated_at: datetime
