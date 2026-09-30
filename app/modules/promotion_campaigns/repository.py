import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_campaigns.model import (
    PromotionCampaign,
)


class PromotionCampaignRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR CAMPAÑAS
    #
    # Podemos filtrar opcionalmente por estado:
    #
    # DRAFT
    # ACTIVE
    # EXPIRED
    # CANCELLED
    # ============================================================

    async def find_all(
        self,
        status: str | None = None,
    ) -> list[PromotionCampaign]:

        query = select(
            PromotionCampaign
        )

        if status is not None:
            query = query.where(
                PromotionCampaign.status == status
            )

        query = query.order_by(
            PromotionCampaign.start_date.desc(),
            PromotionCampaign.created_at.desc(),
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
        campaign_id: uuid.UUID,
    ) -> PromotionCampaign | None:

        query = select(
            PromotionCampaign
        ).where(
            PromotionCampaign.id == campaign_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        name: str,
        description: str | None,
        start_date,
        end_date,
        status: str,
        stackable: bool,
    ) -> PromotionCampaign:

        campaign = PromotionCampaign(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status,
            stackable=stackable,
        )

        self.db.add(
            campaign
        )

        await self.db.flush()
        await self.db.refresh(
            campaign
        )

        return campaign

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        campaign: PromotionCampaign,
        data: dict,
    ) -> PromotionCampaign:

        for field, value in data.items():
            setattr(
                campaign,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(
            campaign
        )

        return campaign