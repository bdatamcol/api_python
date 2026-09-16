import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.specification_definitions.model import (
    SpecificationDefinition,
)


class SpecificationDefinitionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR TODAS LAS DEFINICIONES
    # ============================================================

    async def find_all(
        self,
    ) -> list[SpecificationDefinition]:

        query = (
            select(SpecificationDefinition)
            .order_by(
                SpecificationDefinition.name.asc()
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
        specification_id: uuid.UUID,
    ) -> SpecificationDefinition | None:

        query = select(
            SpecificationDefinition
        ).where(
            SpecificationDefinition.id
            == specification_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE
    # ============================================================

    async def find_by_name(
        self,
        name: str,
    ) -> SpecificationDefinition | None:

        query = select(
            SpecificationDefinition
        ).where(
            SpecificationDefinition.name == name
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR SLUG
    # ============================================================

    async def find_by_slug(
        self,
        slug: str,
    ) -> SpecificationDefinition | None:

        query = select(
            SpecificationDefinition
        ).where(
            SpecificationDefinition.slug == slug
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        name: str,
        slug: str,
        unit: str | None,
        data_type: str,
    ) -> SpecificationDefinition:

        specification = SpecificationDefinition(
            name=name,
            slug=slug,
            unit=unit,
            data_type=data_type,
        )

        self.db.add(
            specification
        )

        await self.db.flush()
        await self.db.refresh(
            specification
        )

        return specification

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        specification: SpecificationDefinition,
        data: dict,
    ) -> SpecificationDefinition:

        for field, value in data.items():
            setattr(
                specification,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(
            specification
        )

        return specification