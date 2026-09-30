import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    model_validator,
)


# ============================================================
# MIXIN DE VALORES
#
# Una especificación solamente puede tener UNO de estos:
#
# value_text
# value_number
# value_boolean
# value_json
# ============================================================

class SpecValueFields(BaseModel):
    value_text: str | None = None

    value_number: Decimal | None = Field(
        default=None,
        max_digits=18,
        decimal_places=4,
    )

    value_boolean: bool | None = None

    value_json: JsonValue | None = None

    @model_validator(mode="after")
    def validate_single_value(self):
        values = [
            self.value_text,
            self.value_number,
            self.value_boolean,
            self.value_json,
        ]

        non_null_values = sum(
            value is not None
            for value in values
        )

        if non_null_values != 1:
            raise ValueError(
                "Debe enviarse exactamente un valor entre "
                "value_text, value_number, value_boolean o value_json"
            )

        return self


# ============================================================
# CREATE COMPLETO
#
# Útil internamente si alguna vez necesitamos enviar también
# model_id directamente.
# ============================================================

class ModelSpecValueCreate(
    SpecValueFields
):
    model_id: uuid.UUID

    specification_id: uuid.UUID


# ============================================================
# CREATE DESDE UNA MOTOCICLETA
#
# Lo usaremos con:
#
# POST /motorcycles/{motorcycle_id}/specifications
#
# El model_id vendrá en la URL.
# ============================================================

class ModelSpecValueCreateForModel(
    SpecValueFields
):
    specification_id: uuid.UUID


# ============================================================
# UPDATE
#
# Para actualizar una especificación también exigimos que llegue
# exactamente un valor.
#
# El service posteriormente limpiará los otros value_* antes
# de guardar.
# ============================================================

class ModelSpecValueUpdate(
    SpecValueFields
):
    pass


# ============================================================
# RESPONSE
# ============================================================

class ModelSpecValueResponse(
    SpecValueFields
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    model_id: uuid.UUID

    specification_id: uuid.UUID

    created_at: datetime

    updated_at: datetime