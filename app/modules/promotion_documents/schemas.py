import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
)


PromotionDocumentType = Literal[
    "IMAGE",
    "PDF",
    "EXCEL",
    "EMAIL",
    "WORD",
    "OTHER",
]


# ============================================================
# BASE
# ============================================================

class PromotionDocumentBase(BaseModel):
    campaign_id: uuid.UUID

    document_type: PromotionDocumentType

    original_name: str | None = Field(
        default=None,
        max_length=255,
        examples=["comunicado_promocion_septiembre.pdf"],
    )

    storage_key: str | None = Field(
        default=None,
        examples=[
            "promotions/2026/septiembre/comunicado.pdf"
        ],
    )

    source_url: str | None = None

    received_at: datetime | None = None

    notes: str | None = None

    metadata: Any | None = None


# ============================================================
# CREATE COMPLETO
# ============================================================

class PromotionDocumentCreate(
    PromotionDocumentBase
):
    pass


# ============================================================
# CREATE DESDE UNA CAMPAÑA
#
# Lo usaremos posteriormente con:
#
# POST /promotion-campaigns/{campaign_id}/documents
#
# campaign_id viene desde la URL.
# ============================================================

class PromotionDocumentCreateForCampaign(
    BaseModel
):
    document_type: PromotionDocumentType

    original_name: str | None = Field(
        default=None,
        max_length=255,
        examples=["comunicado_promocion_septiembre.pdf"],
    )

    storage_key: str | None = None

    source_url: str | None = None

    received_at: datetime | None = None

    notes: str | None = None

    metadata: Any | None = None


# ============================================================
# UPDATE
#
# Todos son opcionales porque utilizaremos PATCH.
#
# El service deberá utilizar model_fields_set para distinguir:
#
# {}
#
# de:
#
# {"notes": null}
#
# o:
#
# {"storage_key": null}
# ============================================================

class PromotionDocumentUpdate(
    BaseModel
):
    document_type: PromotionDocumentType | None = None

    original_name: str | None = Field(
        default=None,
        max_length=255,
    )

    storage_key: str | None = None

    source_url: str | None = None

    received_at: datetime | None = None

    notes: str | None = None

    metadata: Any | None = None


# ============================================================
# RESPONSE
#
# IMPORTANTE:
#
# En PostgreSQL la columna se llama:
#
# metadata
#
# Pero en el modelo SQLAlchemy tuvimos que usar:
#
# metadata_json
#
# porque "metadata" está reservado por SQLAlchemy.
#
# Con validation_alias hacemos que Pydantic lea
# metadata_json del ORM pero la API siga respondiendo:
#
# "metadata": {...}
# ============================================================

class PromotionDocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    campaign_id: uuid.UUID

    document_type: PromotionDocumentType

    original_name: str | None
    storage_key: str | None
    source_url: str | None

    received_at: datetime | None

    notes: str | None

    metadata: Any | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "metadata_json",
            "metadata",
        ),
    )

    created_at: datetime
