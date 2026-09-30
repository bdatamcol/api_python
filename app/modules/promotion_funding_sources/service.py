import re
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_funding_sources.model import (
    PromotionFundingSource,
)
from app.modules.promotion_funding_sources.repository import (
    PromotionFundingSourceRepository,
)
from app.modules.promotion_funding_sources.schemas import (
    PromotionFundingSourceCreate,
    PromotionFundingSourceUpdate,
)


class PromotionFundingSourceService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionFundingSourceRepository(
            db
        )

    # ============================================================
    # LISTAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[PromotionFundingSource]:

        return await self.repository.find_all(
            active=active
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        funding_source_id: uuid.UUID,
    ) -> PromotionFundingSource:

        funding_source = (
            await self.repository.find_by_id(
                funding_source_id
            )
        )

        if funding_source is None:
            raise LookupError(
                "La fuente de financiación no existe"
            )

        return funding_source

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: PromotionFundingSourceCreate,
    ) -> PromotionFundingSource:

        # ========================================================
        # NORMALIZAR
        # ========================================================

        name = self._clean_name(
            data.name
        )

        code = self._clean_code(
            data.code
        )

        # ========================================================
        # VALIDAR NOMBRE
        # ========================================================

        existing_name = await self.repository.find_by_name(
            name
        )

        if existing_name is not None:
            raise ValueError(
                "Ya existe una fuente de financiación con ese nombre"
            )

        # ========================================================
        # VALIDAR CODIGO
        # ========================================================

        existing_code = await self.repository.find_by_code(
            code
        )

        if existing_code is not None:
            raise ValueError(
                "Ya existe una fuente de financiación con ese código"
            )

        try:
            funding_source = await self.repository.create(
                name=name,
                code=code,
            )

            await self.db.commit()

            await self.db.refresh(
                funding_source
            )

            return funding_source

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear la fuente de financiación porque el nombre o código ya existe"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        funding_source_id: uuid.UUID,
        data: PromotionFundingSourceUpdate,
    ) -> PromotionFundingSource:

        funding_source = (
            await self.repository.find_by_id(
                funding_source_id
            )
        )

        if funding_source is None:
            raise LookupError(
                "La fuente de financiación no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return funding_source

        # ========================================================
        # NOMBRE
        # ========================================================

        if "name" in update_data:

            if update_data["name"] is None:
                raise ValueError(
                    "El nombre no puede ser nulo"
                )

            name = self._clean_name(
                update_data["name"]
            )

            existing_name = (
                await self.repository.find_by_name(
                    name
                )
            )

            if (
                existing_name is not None
                and existing_name.id
                != funding_source.id
            ):
                raise ValueError(
                    "Ya existe una fuente de financiación con ese nombre"
                )

            update_data["name"] = name

        # ========================================================
        # CODIGO
        # ========================================================

        if "code" in update_data:

            if update_data["code"] is None:
                raise ValueError(
                    "El código no puede ser nulo"
                )

            code = self._clean_code(
                update_data["code"]
            )

            existing_code = (
                await self.repository.find_by_code(
                    code
                )
            )

            if (
                existing_code is not None
                and existing_code.id
                != funding_source.id
            ):
                raise ValueError(
                    "Ya existe una fuente de financiación con ese código"
                )

            update_data["code"] = code

        # ========================================================
        # ACTIVE
        # ========================================================

        if (
            "active" in update_data
            and update_data["active"] is None
        ):
            raise ValueError(
                "El estado activo no puede ser nulo"
            )

        try:
            funding_source = (
                await self.repository.update(
                    funding_source=funding_source,
                    data=update_data,
                )
            )

            await self.db.commit()

            await self.db.refresh(
                funding_source
            )

            return funding_source

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar la fuente de financiación porque el nombre o código entra en conflicto con otro registro"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    #
    # No eliminamos físicamente.
    # ============================================================

    async def deactivate(
        self,
        funding_source_id: uuid.UUID,
    ) -> PromotionFundingSource:

        funding_source = (
            await self.repository.find_by_id(
                funding_source_id
            )
        )

        if funding_source is None:
            raise LookupError(
                "La fuente de financiación no existe"
            )

        if not funding_source.active:
            return funding_source

        try:
            funding_source = (
                await self.repository.update(
                    funding_source=funding_source,
                    data={
                        "active": False,
                    },
                )
            )

            await self.db.commit()

            await self.db.refresh(
                funding_source
            )

            return funding_source

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # NORMALIZAR NOMBRE
    # ============================================================

    @staticmethod
    def _clean_name(
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
                "El nombre no puede estar vacío"
            )

        return value

    # ============================================================
    # NORMALIZAR CODIGO
    #
    # " manufacturer "
    #
    # ->
    #
    # "MANUFACTURER"
    # ============================================================

    @staticmethod
    def _clean_code(
        value: str,
    ) -> str:

        value = value.strip().upper()

        value = re.sub(
            r"\s+",
            "_",
            value,
        )

        if not value:
            raise ValueError(
                "El código no puede estar vacío"
            )

        return value