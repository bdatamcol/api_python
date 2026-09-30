import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_funding.model import (
    PromotionRuleFunding,
)


class PromotionRuleFundingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR FUENTES DE FINANCIACION DE UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleFunding]:

        query = (
            select(PromotionRuleFunding)
            .where(
                PromotionRuleFunding.promotion_rule_id
                == promotion_rule_id
            )
            .order_by(
                PromotionRuleFunding.funding_source_id.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UNA FUENTE
    # ============================================================

    async def find_all_by_funding_source(
        self,
        funding_source_id: uuid.UUID,
    ) -> list[PromotionRuleFunding]:

        query = (
            select(PromotionRuleFunding)
            .where(
                PromotionRuleFunding.funding_source_id
                == funding_source_id
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR RELACION:
    #
    # promotion_rule_id + funding_source_id
    #
    # Esta combinación forma la PK compuesta.
    # ============================================================

    async def find_by_rule_and_funding_source(
        self,
        promotion_rule_id: uuid.UUID,
        funding_source_id: uuid.UUID,
    ) -> PromotionRuleFunding | None:

        query = select(
            PromotionRuleFunding
        ).where(
            PromotionRuleFunding.promotion_rule_id
            == promotion_rule_id,

            PromotionRuleFunding.funding_source_id
            == funding_source_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR RELACION
    # ============================================================

    async def create(
        self,
        promotion_rule_id: uuid.UUID,
        funding_source_id: uuid.UUID,
        amount: int | None = None,
        percentage: Decimal | None = None,
    ) -> PromotionRuleFunding:

        rule_funding = PromotionRuleFunding(
            promotion_rule_id=promotion_rule_id,
            funding_source_id=funding_source_id,
            amount=amount,
            percentage=percentage,
        )

        self.db.add(
            rule_funding
        )

        await self.db.flush()
        await self.db.refresh(
            rule_funding
        )

        return rule_funding

    # ============================================================
    # ACTUALIZAR APORTE
    #
    # Aquí podemos cambiar:
    #
    # amount
    # percentage
    #
    # No cambiamos las llaves de la relación.
    # ============================================================

    async def update(
        self,
        rule_funding: PromotionRuleFunding,
        *,
        amount: int | None,
        percentage: Decimal | None,
    ) -> PromotionRuleFunding:

        rule_funding.amount = amount
        rule_funding.percentage = percentage

        await self.db.flush()
        await self.db.refresh(
            rule_funding
        )

        return rule_funding

    # ============================================================
    # ELIMINAR RELACION
    #
    # Solamente elimina el aporte de esa fuente para esa regla.
    #
    # NO elimina:
    # - la regla promocional
    # - la fuente de financiación
    # ============================================================

    async def delete(
        self,
        rule_funding: PromotionRuleFunding,
    ) -> None:

        await self.db.delete(
            rule_funding
        )

        await self.db.flush()
