import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_colors.model import (
    PromotionRuleColor,
)


class PromotionRuleColorRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR COLORES ASOCIADOS A UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleColor]:

        query = (
            select(PromotionRuleColor)
            .where(
                PromotionRuleColor.promotion_rule_id
                == promotion_rule_id
            )
            .order_by(
                PromotionRuleColor.color_id.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UN COLOR
    # ============================================================

    async def find_all_by_color(
        self,
        color_id: uuid.UUID,
    ) -> list[PromotionRuleColor]:

        query = (
            select(PromotionRuleColor)
            .where(
                PromotionRuleColor.color_id
                == color_id
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR RELACION REGLA + COLOR
    #
    # Esta combinación forma la PK compuesta.
    # ============================================================

    async def find_by_rule_and_color(
        self,
        promotion_rule_id: uuid.UUID,
        color_id: uuid.UUID,
    ) -> PromotionRuleColor | None:

        query = select(
            PromotionRuleColor
        ).where(
            PromotionRuleColor.promotion_rule_id
            == promotion_rule_id,

            PromotionRuleColor.color_id
            == color_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR RELACION
    # ============================================================

    async def create(
        self,
        promotion_rule_id: uuid.UUID,
        color_id: uuid.UUID,
    ) -> PromotionRuleColor:

        rule_color = PromotionRuleColor(
            promotion_rule_id=promotion_rule_id,
            color_id=color_id,
        )

        self.db.add(
            rule_color
        )

        await self.db.flush()
        await self.db.refresh(
            rule_color
        )

        return rule_color

    # ============================================================
    # ELIMINAR RELACION
    #
    # Solamente elimina la asociación.
    #
    # NO elimina:
    # - la regla promocional
    # - el color
    # ============================================================

    async def delete(
        self,
        rule_color: PromotionRuleColor,
    ) -> None:

        await self.db.delete(
            rule_color
        )

        await self.db.flush()