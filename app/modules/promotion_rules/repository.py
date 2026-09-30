import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rules.model import PromotionRule


class PromotionRuleRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR REGLAS
    #
    # Permite filtrar por:
    #
    # campaign_id
    # active
    # benefit_type
    # ============================================================

    async def find_all(
        self,
        campaign_id: uuid.UUID | None = None,
        active: bool | None = None,
        benefit_type: str | None = None,
    ) -> list[PromotionRule]:

        query = select(PromotionRule)

        if campaign_id is not None:
            query = query.where(
                PromotionRule.campaign_id == campaign_id
            )

        if active is not None:
            query = query.where(
                PromotionRule.active == active
            )

        if benefit_type is not None:
            query = query.where(
                PromotionRule.benefit_type == benefit_type
            )

        query = query.order_by(
            PromotionRule.priority.asc(),
            PromotionRule.created_at.asc(),
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR REGLAS DE UNA CAMPAÑA
    # ============================================================

    async def find_all_by_campaign(
        self,
        campaign_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[PromotionRule]:

        query = select(PromotionRule).where(
            PromotionRule.campaign_id == campaign_id
        )

        if active is not None:
            query = query.where(
                PromotionRule.active == active
            )

        query = query.order_by(
            PromotionRule.priority.asc(),
            PromotionRule.created_at.asc(),
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
        rule_id: uuid.UUID,
    ) -> PromotionRule | None:

        query = select(PromotionRule).where(
            PromotionRule.id == rule_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        campaign_id: uuid.UUID,
        name: str | None,
        benefit_type: str,
        benefit_amount: int | None,
        benefit_percentage: Decimal | None,
        gift_description: str | None,
        terms: str | None,
        priority: int,
        active: bool,
    ) -> PromotionRule:

        rule = PromotionRule(
            campaign_id=campaign_id,
            name=name,
            benefit_type=benefit_type,
            benefit_amount=benefit_amount,
            benefit_percentage=benefit_percentage,
            gift_description=gift_description,
            terms=terms,
            priority=priority,
            active=active,
        )

        self.db.add(rule)

        await self.db.flush()
        await self.db.refresh(rule)

        return rule

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        rule: PromotionRule,
        data: dict,
    ) -> PromotionRule:

        for field, value in data.items():
            setattr(
                rule,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(rule)

        return rule