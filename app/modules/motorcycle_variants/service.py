import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.colors.repository import ColorRepository
from app.modules.motorcycle_variants.model import MotorcycleVariant
from app.modules.motorcycle_variants.repository import (
    MotorcycleVariantRepository,
)
from app.modules.motorcycle_variants.schemas import (
    MotorcycleVariantCreateForModel,
    MotorcycleVariantUpdate,
    VariantSourceSystem,
)
from app.modules.motorcycles.repository import MotorcycleRepository


class MotorcycleVariantService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = MotorcycleVariantRepository(db)
        self.motorcycle_repository = MotorcycleRepository(db)
        self.color_repository = ColorRepository(db)

    # ============================================================
    # LISTAR VARIANTES DE UNA MOTOCICLETA
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[MotorcycleVariant]:

        await self._validate_motorcycle(
            model_id
        )

        return await self.repository.find_all_by_model(
            model_id=model_id,
            active=active,
        )

    # ============================================================
    # BUSCAR VARIANTE POR ID
    # ============================================================

    async def find_by_id(
        self,
        variant_id: uuid.UUID,
    ) -> MotorcycleVariant:

        variant = await self.repository.find_by_id(
            variant_id
        )

        if variant is None:
            raise LookupError(
                "La variante no existe"
            )

        return variant

    # ============================================================
    # CREAR VARIANTE PARA UNA MOTOCICLETA
    # ============================================================

    async def create_for_model(
        self,
        model_id: uuid.UUID,
        data: MotorcycleVariantCreateForModel,
    ) -> MotorcycleVariant:

        # ========================================================
        # VALIDAR MOTOCICLETA
        # ========================================================

        motorcycle = await self._validate_motorcycle(
            model_id
        )

        # ========================================================
        # VALIDAR COLOR
        # ========================================================

        if data.color_id is not None:
            await self._validate_color(
                data.color_id
            )

        # ========================================================
        # NORMALIZAR CAMPOS
        # ========================================================

        sku = (
            data.sku.strip().upper()
            if data.sku
            else None
        )

        external_code = (
            data.external_code.strip().upper()
            if data.external_code
            else None
        )

        commercial_name = (
            data.commercial_name.strip()
            if data.commercial_name
            else None
        )

        # ========================================================
        # VALIDAR SKU UNICO
        # ========================================================

        if sku is not None:

            existing_sku = (
                await self.repository.find_by_sku(
                    sku
                )
            )

            if existing_sku is not None:
                raise ValueError(
                    "Ya existe una variante con ese SKU"
                )

        # ========================================================
        # VALIDAR COMBINACION MODELO + COLOR + AÑO
        # ========================================================

        existing_variant = (
            await self.repository.find_by_model_color_year(
                model_id=model_id,
                color_id=data.color_id,
                model_year=data.model_year,
            )
        )

        if existing_variant is not None:
            raise ValueError(
                "Ya existe una variante para esa combinación de modelo, color y año"
            )

        # ========================================================
        # GENERAR NOMBRE COMERCIAL SI NO VIENE
        # ========================================================

        if commercial_name is None:

            parts: list[str] = [
                motorcycle.name
            ]

            if data.model_year is not None:
                parts.append(
                    str(data.model_year)
                )

            commercial_name = " ".join(
                parts
            )

        try:
            variant = await self.repository.create(
                model_id=model_id,
                color_id=data.color_id,
                sku=sku,
                model_year=data.model_year,
                commercial_name=commercial_name,
                source_system=data.source_system,
                external_code=external_code,
            )

            await self.db.commit()
            await self.db.refresh(variant)

            return variant

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR VARIANTE
    # ============================================================

    async def update(
        self,
        variant_id: uuid.UUID,
        data: MotorcycleVariantUpdate,
    ) -> MotorcycleVariant:

        variant = await self.repository.find_by_id(
            variant_id
        )

        if variant is None:
            raise LookupError(
                "La variante no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ========================================================
        # VALIDAR COLOR SI CAMBIA
        # ========================================================

        if (
            "color_id" in update_data
            and update_data["color_id"] is not None
        ):
            await self._validate_color(
                update_data["color_id"]
            )

        # ========================================================
        # NORMALIZAR SKU
        # ========================================================

        if "sku" in update_data:

            raw_sku = update_data["sku"]

            sku = (
                raw_sku.strip().upper()
                if raw_sku
                else None
            )

            if sku is not None:

                existing_sku = (
                    await self.repository.find_by_sku(
                        sku
                    )
                )

                if (
                    existing_sku is not None
                    and existing_sku.id != variant.id
                ):
                    raise ValueError(
                        "Ya existe una variante con ese SKU"
                    )

            update_data["sku"] = sku

        # ========================================================
        # NORMALIZAR CODIGO EXTERNO
        # ========================================================

        if "external_code" in update_data:

            raw_external_code = (
                update_data["external_code"]
            )

            update_data["external_code"] = (
                raw_external_code.strip().upper()
                if raw_external_code
                else None
            )

        # ========================================================
        # NORMALIZAR NOMBRE COMERCIAL
        # ========================================================

        if "commercial_name" in update_data:

            raw_commercial_name = (
                update_data["commercial_name"]
            )

            update_data["commercial_name"] = (
                raw_commercial_name.strip()
                if raw_commercial_name
                else None
            )

        # ========================================================
        # VALIDAR COMBINACION FINAL
        # MODELO + COLOR + AÑO
        # ========================================================

        final_color_id = (
            update_data["color_id"]
            if "color_id" in update_data
            else variant.color_id
        )

        final_model_year = (
            update_data["model_year"]
            if "model_year" in update_data
            else variant.model_year
        )

        existing_variant = (
            await self.repository.find_by_model_color_year(
                model_id=variant.model_id,
                color_id=final_color_id,
                model_year=final_model_year,
            )
        )

        if (
            existing_variant is not None
            and existing_variant.id != variant.id
        ):
            raise ValueError(
                "Ya existe una variante para esa combinación de modelo, color y año"
            )

        try:
            variant = await self.repository.update(
                variant,
                update_data,
            )

            await self.db.commit()
            await self.db.refresh(variant)

            return variant

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR VARIANTE
    # ============================================================

    async def deactivate(
        self,
        variant_id: uuid.UUID,
    ) -> MotorcycleVariant:

        variant = await self.repository.find_by_id(
            variant_id
        )

        if variant is None:
            raise LookupError(
                "La variante no existe"
            )

        if not variant.active:
            return variant

        try:
            variant = await self.repository.update(
                variant,
                {
                    "active": False
                },
            )

            await self.db.commit()
            await self.db.refresh(variant)

            return variant

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR MOTOCICLETA
    # ============================================================

    async def _validate_motorcycle(
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

        if not motorcycle.active:
            raise ValueError(
                "La motocicleta seleccionada está inactiva"
            )

        return motorcycle

    # ============================================================
    # VALIDAR COLOR
    # ============================================================

    async def _validate_color(
        self,
        color_id: uuid.UUID,
    ) -> None:

        color = await self.color_repository.find_by_id(
            color_id
        )

        if color is None:
            raise ValueError(
                "El color seleccionado no existe"
            )

        if not color.active:
            raise ValueError(
                "El color seleccionado está inactivo"
            )
