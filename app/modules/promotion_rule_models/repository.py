import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_models.model import (
    PromotionRuleModel,
)


class PromotionRuleModelRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR MODELOS ASOCIADOS A UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleModel]:

        query = (
            select(PromotionRuleModel)
            .where(
                PromotionRuleModel.promotion_rule_id
                == promotion_rule_id
            )
            .order_by(
                PromotionRuleModel.model_id.asc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UN MODELO
    #
    # PostgreSQL tiene índice:
    #
    # idx_promotion_rule_models_model
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
    ) -> list[PromotionRuleModel]:

        query = (
            select(PromotionRuleModel)
            .where(
                PromotionRuleModel.model_id
                == model_id
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR RELACION REGLA + MODELO
    #
    # Esta combinación forma la PK compuesta.
    # ============================================================

    async def find_by_rule_and_model(
        self,
        promotion_rule_id: uuid.UUID,
        model_id: uuid.UUID,
    ) -> PromotionRuleModel | None:

        query = select(
            PromotionRuleModel
        ).where(
            PromotionRuleModel.promotion_rule_id
            == promotion_rule_id,

            PromotionRuleModel.model_id
            == model_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR RELACION
    # ============================================================

    async def create(
        self,
        promotion_rule_id: uuid.UUID,
        model_id: uuid.UUID,
    ) -> PromotionRuleModel:

        rule_model = PromotionRuleModel(
            promotion_rule_id=promotion_rule_id,
            model_id=model_id,
        )

        self.db.add(
            rule_model
        )

        await self.db.flush()
        await self.db.refresh(
            rule_model
        )

        return rule_model

    # ============================================================
    # ELIMINAR RELACION
    #
    # Eliminamos únicamente la asociación.
    #
    # NO se elimina:
    # - la regla
    # - la motocicleta
    # ============================================================

    async def delete(
        self,
        rule_model: PromotionRuleModel,
    ) -> None:

        await self.db.delete(
            rule_model
        )

        await self.db.flush()