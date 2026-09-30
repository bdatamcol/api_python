import uuid
from datetime import datetime
from typing import Any

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# BASE
# ============================================================

class ModelDocumentBase(BaseModel):
    model_id: uuid.UUID

    title: str = Field(
        max_length=250,
        examples=["Ficha técnica SWITCH 125"],
    )

    document_type: str | None = Field(
        default=None,
        max_length=40,
        examples=["FICHA_TECNICA"],
    )

    storage_key: str | None = Field(
        default=None,
        examples=[
            "motorcycles/switch-125/ficha-tecnica.pdf"
        ],
    )

    source_url: str | None = None

    metadata: Any | None = None

    active: bool = True


# ============================================================
# CREATE COMPLETO
# ============================================================

class ModelDocumentCreate(
    ModelDocumentBase
):
    pass


# ============================================================
# CREATE DESDE UN MODELO
#
# Lo usaremos posteriormente con:
#
# POST /motorcycles/{model_id}/documents
#
# model_id viene desde la URL.
# ============================================================

class ModelDocumentCreateForModel(
    BaseModel
):
    title: str = Field(
        max_length=250,
        examples=["Ficha técnica SWITCH 125"],
    )

    document_type: str | None = Field(
        default=None,
        max_length=40,
        examples=["FICHA_TECNICA"],
    )

    storage_key: str | None = None

    source_url: str | None = None

    metadata: Any | None = None

    active: bool = True


# ============================================================
# UPDATE
#
# Usaremos PATCH.
#
# Todos los campos son opcionales para poder modificar
# únicamente lo enviado.
#
# El service deberá usar model_fields_set para distinguir:
#
# {}
#
# de:
#
# {"storage_key": null}
#
# También deberá impedir:
#
# {"title": null}
#
# porque title es NOT NULL en PostgreSQL.
# ============================================================

class ModelDocumentUpdate(
    BaseModel
):
    title: str | None = Field(
        default=None,
        max_length=250,
    )

    document_type: str | None = Field(
        default=None,
        max_length=40,
    )

    storage_key: str | None = None

    source_url: str | None = None

    metadata: Any | None = None

    active: bool | None = None


# ============================================================
# RESPONSE
#
# En PostgreSQL:
#
# metadata
#
# En el modelo SQLAlchemy:
#
# metadata_json
#
# Pydantic leerá metadata_json pero la API seguirá
# exponiendo el campo como "metadata".
# ============================================================

class ModelDocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    model_id: uuid.UUID

    title: str

    document_type: str | None

    storage_key: str | None
    source_url: str | None

    metadata: Any | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "metadata_json",
            "metadata",
        ),
    )

    active: bool

    created_at: datetime
