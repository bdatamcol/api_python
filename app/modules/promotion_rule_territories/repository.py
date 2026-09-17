import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_territories.model import (
    PromotionRuleTerritory,
)


class PromotionRuleTerritoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR TERRITORIOS ASOCIADOS A UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleTerritory]:

        query = (
            select(PromotionRuleTerritory)
            .where(
                PromotionRuleTerritory.promotion_rule_id
                == promotion_rule_id
            )
            .order_by(
                PromotionRuleTerritory.territory_id.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UN TERRITORIO
    # ============================================================

    async def find_all_by_territory(
        self,
        territory_id: uuid.UUID,
    ) -> list[PromotionRuleTerritory]:

        query = (
            select(PromotionRuleTerritory)
            .where(
                PromotionRuleTerritory.territory_id
                == territory_id
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR RELACION REGLA + TERRITORIO
    #
    # Esta combinación forma la PK compuesta.
    # ============================================================

    async def find_by_rule_and_territory(
        self,
        promotion_rule_id: uuid.UUID,
        territory_id: uuid.UUID,
    ) -> PromotionRuleTerritory | None:

        query = select(
            PromotionRuleTerritory
        ).where(
            PromotionRuleTerritory.promotion_rule_id
            == promotion_rule_id,

            PromotionRuleTerritory.territory_id
            == territory_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR RELACION
    # ============================================================

    async def create(
        self,
        promotion_rule_id: uuid.UUID,
        territory_id: uuid.UUID,
    ) -> PromotionRuleTerritory:

        rule_territory = PromotionRuleTerritory(
            promotion_rule_id=promotion_rule_id,
            territory_id=territory_id,
        )

        self.db.add(
            rule_territory
        )

        await self.db.flush()
        await self.db.refresh(
            rule_territory
        )

        return rule_territory

    # ============================================================
    # ELIMINAR RELACION
    #
    # Solo elimina la asociación.
    #
    # NO elimina:
    # - la regla promocional
    # - el territorio
    # ============================================================

    async def delete(
        self,
        rule_territory: PromotionRuleTerritory,
    ) -> None:

        await self.db.delete(
            rule_territory
        )

        await self.db.flush()
