import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_variants.model import (
    PromotionRuleVariant,
)


class PromotionRuleVariantRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR VARIANTES ASOCIADAS A UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleVariant]:

        query = (
            select(PromotionRuleVariant)
            .where(
                PromotionRuleVariant.promotion_rule_id
                == promotion_rule_id
            )
            .order_by(
                PromotionRuleVariant.variant_id.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UNA VARIANTE
    #
    # PostgreSQL tiene índice sobre variant_id.
    # ============================================================

    async def find_all_by_variant(
        self,
        variant_id: uuid.UUID,
    ) -> list[PromotionRuleVariant]:

        query = (
            select(PromotionRuleVariant)
            .where(
                PromotionRuleVariant.variant_id
                == variant_id
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR RELACION REGLA + VARIANTE
    #
    # Esta combinación forma la PK compuesta.
    # ============================================================

    async def find_by_rule_and_variant(
        self,
        promotion_rule_id: uuid.UUID,
        variant_id: uuid.UUID,
    ) -> PromotionRuleVariant | None:

        query = select(
            PromotionRuleVariant
        ).where(
            PromotionRuleVariant.promotion_rule_id
            == promotion_rule_id,

            PromotionRuleVariant.variant_id
            == variant_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR RELACION
    # ============================================================

    async def create(
        self,
        promotion_rule_id: uuid.UUID,
        variant_id: uuid.UUID,
    ) -> PromotionRuleVariant:

        rule_variant = PromotionRuleVariant(
            promotion_rule_id=promotion_rule_id,
            variant_id=variant_id,
        )

        self.db.add(
            rule_variant
        )

        await self.db.flush()
        await self.db.refresh(
            rule_variant
        )

        return rule_variant

    # ============================================================
    # ELIMINAR RELACION
    #
    # Solamente elimina la asociación.
    #
    # NO elimina:
    # - la regla promocional
    # - la variante
    # ============================================================

    async def delete(
        self,
        rule_variant: PromotionRuleVariant,
    ) -> None:

        await self.db.delete(
            rule_variant
        )

        await self.db.flush()