import re
import unicodedata
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motorcycle_aliases.model import MotorcycleAlias
from app.modules.motorcycle_aliases.repository import (
    MotorcycleAliasRepository,
)
from app.modules.motorcycle_aliases.schemas import (
    MotorcycleAliasCreateForModel,
    MotorcycleAliasUpdate,
)
from app.modules.motorcycles.repository import MotorcycleRepository


class MotorcycleAliasService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = MotorcycleAliasRepository(db)
        self.motorcycle_repository = MotorcycleRepository(db)

    # ============================================================
    # LISTAR ALIAS DE UNA MOTOCICLETA
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
    ) -> list[MotorcycleAlias]:

        await self._validate_motorcycle(
            model_id
        )

        return await self.repository.find_all_by_model(
            model_id
        )

    # ============================================================
    # BUSCAR ALIAS POR ID
    # ============================================================

    async def find_by_id(
        self,
        alias_id: uuid.UUID,
    ) -> MotorcycleAlias:

        motorcycle_alias = (
            await self.repository.find_by_id(
                alias_id
            )
        )

        if motorcycle_alias is None:
            raise LookupError(
                "El alias no existe"
            )

        return motorcycle_alias

    # ============================================================
    # CREAR ALIAS PARA UNA MOTOCICLETA
    # ============================================================

    async def create_for_model(
        self,
        model_id: uuid.UUID,
        data: MotorcycleAliasCreateForModel,
    ) -> MotorcycleAlias:

        await self._validate_motorcycle(
            model_id
        )

        alias = self._clean_alias(
            data.alias
        )

        normalized_alias = self._normalize_alias(
            alias
        )

        existing_alias = (
            await self.repository.find_by_normalized_alias(
                model_id=model_id,
                normalized_alias=normalized_alias,
            )
        )

        if existing_alias is not None:
            raise ValueError(
                "La motocicleta ya tiene registrado ese alias"
            )

        try:
            motorcycle_alias = (
                await self.repository.create(
                    model_id=model_id,
                    alias=alias,
                    normalized_alias=normalized_alias,
                )
            )

            await self.db.commit()
            await self.db.refresh(
                motorcycle_alias
            )

            return motorcycle_alias

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR ALIAS
    # ============================================================

    async def update(
        self,
        alias_id: uuid.UUID,
        data: MotorcycleAliasUpdate,
    ) -> MotorcycleAlias:

        motorcycle_alias = (
            await self.repository.find_by_id(
                alias_id
            )
        )

        if motorcycle_alias is None:
            raise LookupError(
                "El alias no existe"
            )

        alias = self._clean_alias(
            data.alias
        )

        normalized_alias = self._normalize_alias(
            alias
        )

        existing_alias = (
            await self.repository.find_by_normalized_alias(
                model_id=motorcycle_alias.model_id,
                normalized_alias=normalized_alias,
            )
        )

        if (
            existing_alias is not None
            and existing_alias.id != motorcycle_alias.id
        ):
            raise ValueError(
                "La motocicleta ya tiene registrado ese alias"
            )

        try:
            motorcycle_alias = (
                await self.repository.update(
                    motorcycle_alias=motorcycle_alias,
                    alias=alias,
                    normalized_alias=normalized_alias,
                )
            )

            await self.db.commit()
            await self.db.refresh(
                motorcycle_alias
            )

            return motorcycle_alias

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR ALIAS
    # ============================================================

    async def delete(
        self,
        alias_id: uuid.UUID,
    ) -> None:

        motorcycle_alias = (
            await self.repository.find_by_id(
                alias_id
            )
        )

        if motorcycle_alias is None:
            raise LookupError(
                "El alias no existe"
            )

        try:
            await self.repository.delete(
                motorcycle_alias
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR MOTOCICLETA
    # ============================================================

    async def _validate_motorcycle(
        self,
        model_id: uuid.UUID,
    ) -> None:

        motorcycle = (
            await self.motorcycle_repository.find_by_id(
                model_id
            )
        )

        if motorcycle is None:
            raise ValueError(
                "La motocicleta seleccionada no existe"
            )

        if not motorcycle.active:
            raise ValueError(
                "La motocicleta seleccionada está inactiva"
            )

    # ============================================================
    # LIMPIAR ALIAS PARA MOSTRAR
    #
    # "  Victory   Switch  125 "
    #
    # ->
    #
    # "Victory Switch 125"
    # ============================================================

    @staticmethod
    def _clean_alias(
        alias: str,
    ) -> str:

        alias = alias.strip()

        alias = re.sub(
            r"\s+",
            " ",
            alias,
        )

        if not alias:
            raise ValueError(
                "El alias no puede estar vacío"
            )

        return alias

    # ============================================================
    # NORMALIZAR ALIAS PARA BUSQUEDAS
    #
    # "  Víctory   SWITCH 125 "
    #
    # ->
    #
    # "victory switch 125"
    # ============================================================

    @staticmethod
    def _normalize_alias(
        alias: str,
    ) -> str:

        value = alias.lower().strip()

        # Quitar acentos
        value = unicodedata.normalize(
            "NFKD",
            value,
        )

        value = "".join(
            character
            for character in value
            if not unicodedata.combining(
                character
            )
        )

        # Convertir multiples espacios en uno
        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value
