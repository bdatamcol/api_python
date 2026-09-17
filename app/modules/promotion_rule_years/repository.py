import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_years.model import (
    PromotionRuleYear,
)


class PromotionRuleYearRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR AÑOS ASOCIADOS A UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleYear]:

        query = (
            select(PromotionRuleYear)
            .where(
                PromotionRuleYear.promotion_rule_id
                == promotion_rule_id
            )
            .order_by(
                PromotionRuleYear.model_year.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR RELACION REGLA + AÑO
    #
    # Esta combinación forma la PK compuesta.
    # ============================================================

    async def find_by_rule_and_year(
        self,
        promotion_rule_id: uuid.UUID,
        model_year: int,
    ) -> PromotionRuleYear | None:

        query = select(
            PromotionRuleYear
        ).where(
            PromotionRuleYear.promotion_rule_id
            == promotion_rule_id,

            PromotionRuleYear.model_year
            == model_year,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR RELACION
    # ============================================================

    async def create(
        self,
        promotion_rule_id: uuid.UUID,
        model_year: int,
    ) -> PromotionRuleYear:

        rule_year = PromotionRuleYear(
            promotion_rule_id=promotion_rule_id,
            model_year=model_year,
        )

        self.db.add(
            rule_year
        )

        await self.db.flush()
        await self.db.refresh(
            rule_year
        )

        return rule_year

    # ============================================================
    # ELIMINAR RELACION
    #
    # Solamente quitamos el año de la regla.
    # No eliminamos la regla promocional.
    # ============================================================

    async def delete(
        self,
        rule_year: PromotionRuleYear,
    ) -> None:

        await self.db.delete(
            rule_year
        )

        await self.db.flush()