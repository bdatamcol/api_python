import re
import uuid

from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.specification_definitions.model import (
    SpecificationDefinition,
)
from app.modules.specification_definitions.repository import (
    SpecificationDefinitionRepository,
)
from app.modules.specification_definitions.schemas import (
    SpecificationDataType,
    SpecificationDefinitionCreate,
    SpecificationDefinitionUpdate,
)


class SpecificationDefinitionService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = SpecificationDefinitionRepository(
            db
        )

    # ============================================================
    # LISTAR TODAS LAS ESPECIFICACIONES
    # ============================================================

    async def find_all(
        self,
    ) -> list[SpecificationDefinition]:

        return await self.repository.find_all()

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        specification_id: uuid.UUID,
    ) -> SpecificationDefinition:

        specification = (
            await self.repository.find_by_id(
                specification_id
            )
        )

        if specification is None:
            raise LookupError(
                "La definición de especificación no existe"
            )

        return specification

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: SpecificationDefinitionCreate,
    ) -> SpecificationDefinition:

        # ========================================================
        # NORMALIZAR NOMBRE
        # ========================================================

        name = self._clean_required_text(
            data.name
        )

        # ========================================================
        # GENERAR SLUG
        #
        # "Capacidad del tanque"
        #
        # ->
        #
        # "capacidad-del-tanque"
        # ========================================================

        generated_slug = slugify(
            name
        )

        # ========================================================
        # VALIDAR SLUG DUPLICADO
        #
        # En PostgreSQL slug tiene UNIQUE.
        # ========================================================

        existing_slug = (
            await self.repository.find_by_slug(
                generated_slug
            )
        )

        if existing_slug is not None:
            raise ValueError(
                "Ya existe una especificación con ese nombre"
            )

        # ========================================================
        # NORMALIZAR UNIDAD
        # ========================================================

        unit = self._clean_optional_text(
            data.unit
        )

        # ========================================================
        # DATA TYPE
        # ========================================================

        data_type = data.data_type.value

        try:
            specification = (
                await self.repository.create(
                    name=name,
                    slug=generated_slug,
                    unit=unit,
                    data_type=data_type,
                )
            )

            await self.db.commit()

            await self.db.refresh(
                specification
            )

            return specification

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear la especificación porque ya existe un registro con esos datos"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        specification_id: uuid.UUID,
        data: SpecificationDefinitionUpdate,
    ) -> SpecificationDefinition:

        specification = (
            await self.repository.find_by_id(
                specification_id
            )
        )

        if specification is None:
            raise LookupError(
                "La definición de especificación no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return specification

        # ========================================================
        # ACTUALIZAR NOMBRE
        #
        # Si cambia el nombre también regeneramos el slug.
        # ========================================================

        if "name" in update_data:

            if update_data["name"] is None:
                raise ValueError(
                    "El nombre no puede ser nulo"
                )

            name = self._clean_required_text(
                update_data["name"]
            )

            generated_slug = slugify(
                name
            )

            existing_slug = (
                await self.repository.find_by_slug(
                    generated_slug
                )
            )

            if (
                existing_slug is not None
                and existing_slug.id != specification.id
            ):
                raise ValueError(
                    "Ya existe una especificación con ese nombre"
                )

            update_data["name"] = name
            update_data["slug"] = generated_slug

        # ========================================================
        # ACTUALIZAR UNIDAD
        #
        # Se permite NULL.
        # ========================================================

        if "unit" in update_data:
            update_data["unit"] = (
                self._clean_optional_text(
                    update_data["unit"]
                )
            )

        # ========================================================
        # ACTUALIZAR TIPO
        # ========================================================

        if "data_type" in update_data:

            if update_data["data_type"] is None:
                raise ValueError(
                    "El tipo de dato no puede ser nulo"
                )

            if isinstance(
                update_data["data_type"],
                SpecificationDataType,
            ):
                update_data["data_type"] = (
                    update_data["data_type"].value
                )

        try:
            specification = (
                await self.repository.update(
                    specification=specification,
                    data=update_data,
                )
            )

            await self.db.commit()

            await self.db.refresh(
                specification
            )

            return specification

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar la especificación porque los datos entran en conflicto con otro registro"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # LIMPIAR TEXTO OBLIGATORIO
    # ============================================================

    @staticmethod
    def _clean_required_text(
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
                "El texto no puede estar vacío"
            )

        return value

    # ============================================================
    # LIMPIAR TEXTO OPCIONAL
    # ============================================================

    @staticmethod
    def _clean_optional_text(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value or None