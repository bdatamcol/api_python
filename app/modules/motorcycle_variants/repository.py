import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motorcycle_variants.model import MotorcycleVariant
from app.modules.motorcycle_variants.schemas import VariantSourceSystem


class MotorcycleVariantRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR VARIANTES DE UNA MOTOCICLETA
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[MotorcycleVariant]:

        query = select(MotorcycleVariant).where(
            MotorcycleVariant.model_id == model_id
        )

        if active is not None:
            query = query.where(
                MotorcycleVariant.active == active
            )

        query = query.order_by(
            MotorcycleVariant.model_year.desc(),
            MotorcycleVariant.commercial_name.asc(),
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
        variant_id: uuid.UUID,
    ) -> MotorcycleVariant | None:

        query = select(MotorcycleVariant).where(
            MotorcycleVariant.id == variant_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR SKU
    # ============================================================

    async def find_by_sku(
        self,
        sku: str,
    ) -> MotorcycleVariant | None:

        query = select(MotorcycleVariant).where(
            MotorcycleVariant.sku == sku
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR CODIGO EXTERNO
    # ============================================================

    async def find_by_external_code(
        self,
        external_code: str,
    ) -> list[MotorcycleVariant]:

        query = select(MotorcycleVariant).where(
            MotorcycleVariant.external_code == external_code
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR VARIANTE POR MODELO + COLOR + AÑO
    #
    # Nos ayudará a detectar variantes duplicadas.
    # ============================================================

    async def find_by_model_color_year(
        self,
        model_id: uuid.UUID,
        color_id: uuid.UUID | None,
        model_year: int | None,
    ) -> MotorcycleVariant | None:

        query = select(MotorcycleVariant).where(
            MotorcycleVariant.model_id == model_id
        )

        if color_id is None:
            query = query.where(
                MotorcycleVariant.color_id.is_(None)
            )
        else:
            query = query.where(
                MotorcycleVariant.color_id == color_id
            )

        if model_year is None:
            query = query.where(
                MotorcycleVariant.model_year.is_(None)
            )
        else:
            query = query.where(
                MotorcycleVariant.model_year == model_year
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        model_id: uuid.UUID,
        color_id: uuid.UUID | None = None,
        sku: str | None = None,
        model_year: int | None = None,
        commercial_name: str | None = None,
        source_system: VariantSourceSystem = (
            VariantSourceSystem.MANUAL
        ),
        external_code: str | None = None,
    ) -> MotorcycleVariant:

        variant = MotorcycleVariant(
            model_id=model_id,
            color_id=color_id,
            sku=sku,
            model_year=model_year,
            commercial_name=commercial_name,
            source_system=source_system.value,
            external_code=external_code,
        )

        self.db.add(variant)

        await self.db.flush()
        await self.db.refresh(variant)

        return variant

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        variant: MotorcycleVariant,
        data: dict,
    ) -> MotorcycleVariant:

        if (
            "source_system" in data
            and isinstance(
                data["source_system"],
                VariantSourceSystem,
            )
        ):
            data["source_system"] = (
                data["source_system"].value
            )

        for field, value in data.items():
            setattr(
                variant,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(variant)

        return variant
