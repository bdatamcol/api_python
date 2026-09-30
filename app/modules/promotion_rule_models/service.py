import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motorcycles.repository import (
    MotorcycleRepository,
)
from app.modules.promotion_rule_models.model import (
    PromotionRuleModel,
)
from app.modules.promotion_rule_models.repository import (
    PromotionRuleModelRepository,
)
from app.modules.promotion_rule_models.schemas import (
    PromotionRuleModelCreateForRule,
)
from app.modules.promotion_rules.repository import (
    PromotionRuleRepository,
)


class PromotionRuleModelService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionRuleModelRepository(db)

        self.rule_repository = PromotionRuleRepository(db)

        self.motorcycle_repository = MotorcycleRepository(db)

    # ============================================================
    # LISTAR MODELOS DE UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleModel]:

        await self._validate_rule_exists(
            promotion_rule_id
        )

        return await self.repository.find_all_by_rule(
            promotion_rule_id
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UNA MOTOCICLETA
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
    ) -> list[PromotionRuleModel]:

        await self._validate_model_exists(
            model_id
        )

        return await self.repository.find_all_by_model(
            model_id
        )

    # ============================================================
    # ASOCIAR MODELO A UNA REGLA
    # ============================================================

    async def create_for_rule(
        self,
        promotion_rule_id: uuid.UUID,
        data: PromotionRuleModelCreateForRule,
    ) -> PromotionRuleModel:

        # ========================================================
        # VALIDAR REGLA ACTIVA
        # ========================================================

        await self._validate_active_rule(
            promotion_rule_id
        )

        # ========================================================
        # VALIDAR MOTOCICLETA ACTIVA
        # ========================================================

        await self._validate_active_model(
            data.model_id
        )

        # ========================================================
        # EVITAR DUPLICADO
        #
        # promotion_rule_id + model_id
        # es PK compuesta en PostgreSQL.
        # ========================================================

        existing_relation = (
            await self.repository.find_by_rule_and_model(
                promotion_rule_id=promotion_rule_id,
                model_id=data.model_id,
            )
        )

        if existing_relation is not None:
            raise ValueError(
                "La motocicleta ya está asociada a esta regla promocional"
            )

        try:
            rule_model = await self.repository.create(
                promotion_rule_id=promotion_rule_id,
                model_id=data.model_id,
            )

            await self.db.commit()

            await self.db.refresh(
                rule_model
            )

            return rule_model

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible asociar la motocicleta a la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR ASOCIACION
    #
    # No elimina ni la regla ni la motocicleta.
    # Solamente elimina la relación.
    # ============================================================

    async def delete(
        self,
        promotion_rule_id: uuid.UUID,
        model_id: uuid.UUID,
    ) -> None:

        rule_model = (
            await self.repository.find_by_rule_and_model(
                promotion_rule_id=promotion_rule_id,
                model_id=model_id,
            )
        )

        if rule_model is None:
            raise LookupError(
                "La motocicleta no está asociada a esta regla promocional"
            )

        try:
            await self.repository.delete(
                rule_model
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR REGLA
    # ============================================================

    async def _validate_rule_exists(
        self,
        promotion_rule_id: uuid.UUID,
    ):
        rule = await self.rule_repository.find_by_id(
            promotion_rule_id
        )

        if rule is None:
            raise ValueError(
                "La regla promocional seleccionada no existe"
            )

        return rule

    # ============================================================
    # VALIDAR REGLA ACTIVA
    # ============================================================

    async def _validate_active_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ):
        rule = await self._validate_rule_exists(
            promotion_rule_id
        )

        if not rule.active:
            raise ValueError(
                "La regla promocional seleccionada está inactiva"
            )

        return rule

    # ============================================================
    # VALIDAR MOTOCICLETA
    # ============================================================

    async def _validate_model_exists(
        self,
        model_id: uuid.UUID,
    ):
        motorcycle = (
            await self.motorcycle_repository.find_by_id(
                model_id
            )
        )

        if motorcycle is None:
            raise ValueError(
                "La motocicleta seleccionada no existe"
            )

        return motorcycle

    # ============================================================
    # VALIDAR MOTOCICLETA ACTIVA
    # ============================================================

    async def _validate_active_model(
        self,
        model_id: uuid.UUID,
    ):
        motorcycle = await self._validate_model_exists(
            model_id
        )

        if not motorcycle.active:
            raise ValueError(
                "La motocicleta seleccionada está inactiva"
            )

        return motorcycle