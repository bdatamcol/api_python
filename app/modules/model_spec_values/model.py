import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ModelSpecValue(Base):
    __tablename__ = "model_spec_values"

    __table_args__ = (
        UniqueConstraint(
            "model_id",
            "specification_id",
            name="model_spec_values_unique",
        ),
        CheckConstraint(
            """
            num_nonnulls(
                value_text,
                value_number,
                value_boolean,
                value_json
            ) = 1
            """,
            name="model_spec_values_only_one_value",
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
    # MODELO DE MOTOCICLETA
    #
    # Ej:
    # SWITCH 125
    # ============================================================

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "motorcycle_models.id",
            ondelete="CASCADE",
            name="fk_model_spec_values_model",
        ),
        nullable=False,
    )

    # ============================================================
    # DEFINICION DE ESPECIFICACION
    #
    # Ej:
    # Potencia
    # Torque
    # ABS
    # Tipo de freno
    # ============================================================

    specification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "specification_definitions.id",
            ondelete="CASCADE",
            name="fk_model_spec_values_specification",
        ),
        nullable=False,
    )

    # ============================================================
    # VALOR TEXTUAL
    #
    # Para data_type = TEXT
    #
    # Ej:
    # "Disco"
    # "5 velocidades"
    # ============================================================

    value_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # VALOR NUMERICO
    #
    # Para data_type = NUMBER
    #
    # NUMERIC(18,4) exactamente como en PostgreSQL.
    #
    # Ej:
    # 125.0000
    # 10.5000
    # ============================================================

    value_number: Mapped[Decimal | None] = mapped_column(
        Numeric(
            precision=18,
            scale=4,
        ),
        nullable=True,
    )

    # ============================================================
    # VALOR BOOLEANO
    #
    # Para data_type = BOOLEAN
    #
    # Ej:
    # ABS = true
    # ============================================================

    value_boolean: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    # ============================================================
    # VALOR JSON
    #
    # none_as_null=True es importante:
    #
    # Python None
    # ->
    # PostgreSQL NULL
    #
    # y NO:
    #
    # JSONB 'null'
    # ============================================================

    value_json: Mapped[object | None] = mapped_column(
        JSONB(none_as_null=True),
        nullable=True,
    )

    # ============================================================
    # FECHAS
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )