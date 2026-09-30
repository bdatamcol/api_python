import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_funding_sources.model import (
    PromotionFundingSource,
)


class PromotionFundingSourceRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR FUENTES DE FINANCIACION
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[PromotionFundingSource]:

        query = select(
            PromotionFundingSource
        )

        if active is not None:
            query = query.where(
                PromotionFundingSource.active == active
            )

        query = query.order_by(
            PromotionFundingSource.name.asc()
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
        funding_source_id: uuid.UUID,
    ) -> PromotionFundingSource | None:

        query = select(
            PromotionFundingSource
        ).where(
            PromotionFundingSource.id
            == funding_source_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE
    # ============================================================

    async def find_by_name(
        self,
        name: str,
    ) -> PromotionFundingSource | None:

        query = select(
            PromotionFundingSource
        ).where(
            PromotionFundingSource.name == name
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR CODIGO
    # ============================================================

    async def find_by_code(
        self,
        code: str,
    ) -> PromotionFundingSource | None:

        query = select(
            PromotionFundingSource
        ).where(
            PromotionFundingSource.code == code
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        name: str,
        code: str,
    ) -> PromotionFundingSource:

        funding_source = PromotionFundingSource(
            name=name,
            code=code,
        )

        self.db.add(
            funding_source
        )

        await self.db.flush()
        await self.db.refresh(
            funding_source
        )

        return funding_source

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        funding_source: PromotionFundingSource,
        data: dict,
    ) -> PromotionFundingSource:

        for field, value in data.items():
            setattr(
                funding_source,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(
            funding_source
        )

        return funding_source