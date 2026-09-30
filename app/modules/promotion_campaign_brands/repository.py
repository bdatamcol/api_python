import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_campaign_brands.model import (
    PromotionCampaignBrand,
)


class PromotionCampaignBrandRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR MARCAS DE UNA CAMPAÑA
    # ============================================================

    async def find_all_by_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> list[PromotionCampaignBrand]:

        query = (
            select(PromotionCampaignBrand)
            .where(
                PromotionCampaignBrand.campaign_id
                == campaign_id
            )
            .order_by(
                PromotionCampaignBrand.brand_id.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR CAMPAÑAS DE UNA MARCA
    #
    # Aprovecha el índice existente en PostgreSQL:
    #
    # idx_promotion_campaign_brands_brand
    # ============================================================

    async def find_all_by_brand(
        self,
        brand_id: uuid.UUID,
    ) -> list[PromotionCampaignBrand]:

        query = (
            select(PromotionCampaignBrand)
            .where(
                PromotionCampaignBrand.brand_id
                == brand_id
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR RELACION CAMPAÑA + MARCA
    #
    # Como ambos campos forman la PK,
    # como máximo puede existir un registro.
    # ============================================================

    async def find_by_campaign_and_brand(
        self,
        campaign_id: uuid.UUID,
        brand_id: uuid.UUID,
    ) -> PromotionCampaignBrand | None:

        query = select(
            PromotionCampaignBrand
        ).where(
            PromotionCampaignBrand.campaign_id
            == campaign_id,

            PromotionCampaignBrand.brand_id
            == brand_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR RELACION
    # ============================================================

    async def create(
        self,
        campaign_id: uuid.UUID,
        brand_id: uuid.UUID,
    ) -> PromotionCampaignBrand:

        campaign_brand = PromotionCampaignBrand(
            campaign_id=campaign_id,
            brand_id=brand_id,
        )

        self.db.add(
            campaign_brand
        )

        await self.db.flush()
        await self.db.refresh(
            campaign_brand
        )

        return campaign_brand

    # ============================================================
    # ELIMINAR RELACION
    #
    # Aquí sí usamos DELETE físico.
    #
    # No estamos eliminando ni la campaña ni la marca,
    # únicamente quitando la asociación entre ambas.
    # ============================================================

    async def delete(
        self,
        campaign_brand: PromotionCampaignBrand,
    ) -> None:

        await self.db.delete(
            campaign_brand
        )

        await self.db.flush()