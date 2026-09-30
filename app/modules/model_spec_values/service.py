import re
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.model_spec_values.model import ModelSpecValue
from app.modules.model_spec_values.repository import (
    ModelSpecValueRepository,
)
from app.modules.model_spec_values.schemas import (
    ModelSpecValueCreateForModel,
    ModelSpecValueUpdate,
)
from app.modules.motorcycles.repository import MotorcycleRepository
from app.modules.specification_definitions.repository import (
    SpecificationDefinitionRepository,
)


class ModelSpecValueService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = ModelSpecValueRepository(db)

        self.motorcycle_repository = MotorcycleRepository(db)

        self.specification_repository = (
            SpecificationDefinitionRepository(db)
        )

    # ============================================================
    # LISTAR ESPECIFICACIONES DE UNA MOTOCICLETA
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
    ) -> list[ModelSpecValue]:

        await self._validate_model_exists(
            model_id
        )

        return await self.repository.find_all_by_model(
            model_id
        )

    # ============================================================
    # BUSCAR VALOR POR ID
    # ============================================================

    async def find_by_id(
        self,
        value_id: uuid.UUID,
    ) -> ModelSpecValue:

        specification_value = (
            await self.repository.find_by_id(
                value_id
            )
        )

        if specification_value is None:
            raise LookupError(
                "El valor de especificación no existe"
            )

        return specification_value

    # ============================================================
    # CREAR ESPECIFICACION PARA UNA MOTO
    # ============================================================

    async def create_for_model(
        self,
        model_id: uuid.UUID,
        data: ModelSpecValueCreateForModel,
    ) -> ModelSpecValue:

        # ========================================================
        # VALIDAR MODELO
        # ========================================================

        await self._validate_active_model(
            model_id
        )

        # ========================================================
        # VALIDAR DEFINICION
        # ========================================================

        specification = (
            await self._validate_specification_exists(
                data.specification_id
            )
        )

        # ========================================================
        # EVITAR DUPLICADO
        #
        # model_id + specification_id es UNIQUE en PostgreSQL
        # ========================================================

        existing_value = (
            await self.repository.find_by_model_and_specification(
                model_id=model_id,
                specification_id=data.specification_id,
            )
        )

        if existing_value is not None:
            raise ValueError(
                "La motocicleta ya tiene asignada esta especificación"
            )

        # ========================================================
        # VALIDAR TIPO Y PREPARAR VALOR
        # ========================================================

        value_data = self._build_value_data(
            data_type=specification.data_type,
            data=data,
        )

        try:
            specification_value = (
                await self.repository.create(
                    model_id=model_id,
                    specification_id=data.specification_id,
                    **value_data,
                )
            )

            await self.db.commit()

            await self.db.refresh(
                specification_value
            )

            return specification_value

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible guardar la especificación porque los datos entran en conflicto con otro registro"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR VALOR
    # ============================================================

    async def update(
        self,
        value_id: uuid.UUID,
        data: ModelSpecValueUpdate,
    ) -> ModelSpecValue:

        specification_value = (
            await self.repository.find_by_id(
                value_id
            )
        )

        if specification_value is None:
            raise LookupError(
                "El valor de especificación no existe"
            )

        # ========================================================
        # CONSULTAR DEFINICION PARA CONOCER data_type
        # ========================================================

        specification = (
            await self._validate_specification_exists(
                specification_value.specification_id
            )
        )

        # ========================================================
        # PREPARAR NUEVO VALOR
        #
        # Se limpian los cuatro campos y solamente se guarda
        # el correspondiente al data_type.
        # ========================================================

        value_data = self._build_value_data(
            data_type=specification.data_type,
            data=data,
        )

        try:
            specification_value = (
                await self.repository.update(
                    specification_value=specification_value,
                    data=value_data,
                )
            )

            await self.db.commit()

            await self.db.refresh(
                specification_value
            )

            return specification_value

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar el valor de la especificación"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR ESPECIFICACION DE UNA MOTO
    # ============================================================

    async def delete(
        self,
        value_id: uuid.UUID,
    ) -> None:

        specification_value = (
            await self.repository.find_by_id(
                value_id
            )
        )

        if specification_value is None:
            raise LookupError(
                "El valor de especificación no existe"
            )

        try:
            await self.repository.delete(
                specification_value
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR MODELO
    # ============================================================

    async def _validate_model_exists(
        self,
        model_id: uuid.UUID,
    ):
        motorcycle = (
            await self.motorcycle_repository.find_by_id(
                model_id
            )
        )

        if motorcycle is None:
            raise ValueError(
                "La motocicleta seleccionada no existe"
            )

        return motorcycle

    # ============================================================
    # VALIDAR MODELO ACTIVO
    # ============================================================

    async def _validate_active_model(
        self,
        model_id: uuid.UUID,
    ):
        motorcycle = await self._validate_model_exists(
            model_id
        )

        if not motorcycle.active:
            raise ValueError(
                "La motocicleta seleccionada está inactiva"
            )

        return motorcycle

    # ============================================================
    # VALIDAR DEFINICION
    # ============================================================

    async def _validate_specification_exists(
        self,
        specification_id: uuid.UUID,
    ):
        specification = (
            await self.specification_repository.find_by_id(
                specification_id
            )
        )

        if specification is None:
            raise ValueError(
                "La definición de especificación no existe"
            )

        return specification

    # ============================================================
    # VALIDAR TIPO Y CONSTRUIR VALORES
    #
    # PostgreSQL exige exactamente UNO:
    #
    # value_text
    # value_number
    # value_boolean
    # value_json
    # ============================================================

    def _build_value_data(
        self,
        data_type: str,
        data,
    ) -> dict:

        value_data = {
            "value_text": None,
            "value_number": None,
            "value_boolean": None,
            "value_json": None,
        }

        # ========================================================
        # TEXT
        # ========================================================

        if data_type == "TEXT":

            if data.value_text is None:
                raise ValueError(
                    "Esta especificación requiere value_text"
                )

            value_text = self._clean_text(
                data.value_text
            )

            value_data["value_text"] = value_text

            return value_data

        # ========================================================
        # NUMBER
        # ========================================================

        if data_type == "NUMBER":

            if data.value_number is None:
                raise ValueError(
                    "Esta especificación requiere value_number"
                )

            value_data["value_number"] = (
                data.value_number
            )

            return value_data

        # ========================================================
        # BOOLEAN
        # ========================================================

        if data_type == "BOOLEAN":

            if data.value_boolean is None:
                raise ValueError(
                    "Esta especificación requiere value_boolean"
                )

            value_data["value_boolean"] = (
                data.value_boolean
            )

            return value_data

        # ========================================================
        # JSON
        # ========================================================

        if data_type == "JSON":

            if data.value_json is None:
                raise ValueError(
                    "Esta especificación requiere value_json"
                )

            value_data["value_json"] = (
                data.value_json
            )

            return value_data

        raise ValueError(
            f"Tipo de especificación no soportado: {data_type}"
        )

    # ============================================================
    # NORMALIZAR TEXTO
    # ============================================================

    @staticmethod
    def _clean_text(
        value: str,
    ) -> str:

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        if not value:
            raise ValueError(
                "El valor de texto no puede estar vacío"
            )

        return value