import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.model_spec_values.model import ModelSpecValue


class ModelSpecValueRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR ESPECIFICACIONES DE UNA MOTOCICLETA
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
    ) -> list[ModelSpecValue]:

        query = (
            select(ModelSpecValue)
            .where(
                ModelSpecValue.model_id == model_id
            )
            .order_by(
                ModelSpecValue.created_at.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        value_id: uuid.UUID,
    ) -> ModelSpecValue | None:

        query = select(ModelSpecValue).where(
            ModelSpecValue.id == value_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR MODELO + ESPECIFICACION
    #
    # Esta combinación es UNIQUE en PostgreSQL.
    # ============================================================

    async def find_by_model_and_specification(
        self,
        model_id: uuid.UUID,
        specification_id: uuid.UUID,
    ) -> ModelSpecValue | None:

        query = select(ModelSpecValue).where(
            ModelSpecValue.model_id == model_id,
            ModelSpecValue.specification_id
            == specification_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    #
    # Exactamente uno de los value_* debe contener valor.
    # El service será responsable de garantizarlo.
    # PostgreSQL también lo protege con un CHECK.
    # ============================================================

    async def create(
        self,
        model_id: uuid.UUID,
        specification_id: uuid.UUID,
        value_text: str | None = None,
        value_number: Decimal | None = None,
        value_boolean: bool | None = None,
        value_json: Any | None = None,
    ) -> ModelSpecValue:

        specification_value = ModelSpecValue(
            model_id=model_id,
            specification_id=specification_id,
            value_text=value_text,
            value_number=value_number,
            value_boolean=value_boolean,
            value_json=value_json,
        )

        self.db.add(
            specification_value
        )

        await self.db.flush()
        await self.db.refresh(
            specification_value
        )

        return specification_value

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        specification_value: ModelSpecValue,
        data: dict,
    ) -> ModelSpecValue:

        for field, value in data.items():
            setattr(
                specification_value,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(
            specification_value
        )

        return specification_value

    # ============================================================
    # ELIMINAR VALOR DE ESPECIFICACION
    #
    # Aquí sí tiene sentido borrado físico:
    # estamos quitando una característica asignada a una moto.
    # ============================================================

    async def delete(
        self,
        specification_value: ModelSpecValue,
    ) -> None:

        await self.db.delete(
            specification_value
        )

        await self.db.flush()