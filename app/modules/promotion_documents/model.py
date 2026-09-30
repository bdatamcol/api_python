import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
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


class PromotionDocument(Base):
    __tablename__ = "promotion_documents"

    __table_args__ = (
        CheckConstraint(
            """
            document_type IN (
                'IMAGE',
                'PDF',
                'EXCEL',
                'EMAIL',
                'WORD',
                'OTHER'
            )
            """,
            name="promotion_documents_type_check",
        ),
    )

    # ============================================================
    # ID
    # ============================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # ============================================================
    # CAMPAÑA
    #
    # El documento pertenece directamente a una campaña.
    # ============================================================

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "promotion_campaigns.id",
            ondelete="CASCADE",
            name="fk_promotion_documents_campaign",
        ),
        nullable=False,
    )

    # ============================================================
    # TIPO DE DOCUMENTO
    #
    # Valores permitidos:
    #
    # IMAGE
    # PDF
    # EXCEL
    # EMAIL
    # WORD
    # OTHER
    # ============================================================

    document_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # ============================================================
    # NOMBRE ORIGINAL
    #
    # Ej:
    # comunicado_promocion_septiembre.pdf
    # ============================================================

    original_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ============================================================
    # STORAGE KEY
    #
    # Pensado para almacenamiento tipo MinIO / S3.
    #
    # Ej:
    # promotions/2026/september/documento.pdf
    # ============================================================

    storage_key: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # URL DE ORIGEN
    #
    # Útil si el documento viene de una fuente externa.
    # ============================================================

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # FECHA DE RECEPCION
    #
    # PostgreSQL:
    # TIMESTAMPTZ
    # ============================================================

    received_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    # ============================================================
    # NOTAS
    # ============================================================

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # METADATA
    #
    # IMPORTANTE:
    #
    # No podemos llamar al atributo Python "metadata" porque
    # SQLAlchemy Declarative ya utiliza Base.metadata.
    #
    # Por eso usamos metadata_json en Python, pero lo mapeamos
    # exactamente a la columna PostgreSQL llamada "metadata".
    # ============================================================

    metadata_json: Mapped[object | None] = mapped_column(
        "metadata",
        JSONB(none_as_null=True),
        nullable=True,
    )

    # ============================================================
    # FECHA DE CREACION
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
