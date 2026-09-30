import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    TIMESTAMP,
    UUID,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ModelDocument(Base):
    __tablename__ = "model_documents"

    # ============================================================
    # ID
    # ============================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ============================================================
    # MODELO DE MOTOCICLETA
    #
    # Ej:
    # SWITCH 125
    # APACHE RTR 200
    # RAIDER 125
    # ============================================================

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_models.id",
            ondelete="CASCADE",
            name="fk_model_documents_model",
        ),
        nullable=False,
    )

    # ============================================================
    # TITULO
    #
    # Ej:
    # Ficha técnica SWITCH 125
    # Manual de usuario
    # Brochure comercial
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    # ============================================================
    # TIPO DE DOCUMENTO
    #
    # PostgreSQL:
    # VARCHAR(40) NULL
    #
    # IMPORTANTE:
    # La tabla NO tiene un CHECK con tipos permitidos.
    # No inventamos un enum aquí.
    # ============================================================

    document_type: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    # ============================================================
    # STORAGE KEY
    #
    # Referencia futura al archivo en MinIO / S3.
    #
    # Ej:
    # motorcycles/switch-125/ficha-tecnica.pdf
    # ============================================================

    storage_key: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # URL DE ORIGEN
    # ============================================================

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # METADATA
    #
    # La columna PostgreSQL se llama:
    #
    # metadata
    #
    # Pero "metadata" está reservado por SQLAlchemy Declarative.
    # Por eso utilizamos metadata_json en Python.
    # ============================================================

    metadata_json: Mapped[object | None] = mapped_column(
        "metadata",
        JSONB(none_as_null=True),
        nullable=True,
    )

    # ============================================================
    # ACTIVO
    # ============================================================

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )

    # ============================================================
    # FECHA DE CREACION
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
