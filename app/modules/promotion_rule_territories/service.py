import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_territories.model import (
    PromotionRuleTerritory,
)
from app.modules.promotion_rule_territories.repository import (
    PromotionRuleTerritoryRepository,
)
from app.modules.promotion_rule_territories.schemas import (
    PromotionRuleTerritoryCreateForRule,
)
from app.modules.promotion_rules.repository import (
    PromotionRuleRepository,
)
from app.modules.territories.repository import (
    TerritoryRepository,
)


class PromotionRuleTerritoryService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionRuleTerritoryRepository(db)
        self.rule_repository = PromotionRuleRepository(db)
        self.territory_repository = TerritoryRepository(db)

    # ============================================================
    # LISTAR TERRITORIOS DE UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleTerritory]:

        await self._validate_rule_exists(
            promotion_rule_id
        )

        return await self.repository.find_all_by_rule(
            promotion_rule_id
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UN TERRITORIO
    # ============================================================

    async def find_all_by_territory(
        self,
        territory_id: uuid.UUID,
    ) -> list[PromotionRuleTerritory]:

        await self._validate_territory_exists(
            territory_id
        )

        return await self.repository.find_all_by_territory(
            territory_id
        )

    # ============================================================
    # ASOCIAR TERRITORIO A UNA REGLA
    # ============================================================

    async def create_for_rule(
        self,
        promotion_rule_id: uuid.UUID,
        data: PromotionRuleTerritoryCreateForRule,
    ) -> PromotionRuleTerritory:

        # ========================================================
        # VALIDAR REGLA ACTIVA
        # ========================================================

        await self._validate_active_rule(
            promotion_rule_id
        )

        # ========================================================
        # VALIDAR TERRITORIO ACTIVO
        # ========================================================

        await self._validate_active_territory(
            data.territory_id
        )

        # ========================================================
        # EVITAR DUPLICADOS
        #
        # promotion_rule_id + territory_id
        # es la PK compuesta.
        # ========================================================

        existing_relation = (
            await self.repository.find_by_rule_and_territory(
                promotion_rule_id=promotion_rule_id,
                territory_id=data.territory_id,
            )
        )

        if existing_relation is not None:
            raise ValueError(
                "El territorio ya está asociado a esta regla promocional"
            )

        try:
            rule_territory = await self.repository.create(
                promotion_rule_id=promotion_rule_id,
                territory_id=data.territory_id,
            )

            await self.db.commit()

            await self.db.refresh(
                rule_territory
            )

            return rule_territory

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible asociar el territorio "
                "a la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR TERRITORIO DE UNA REGLA
    #
    # Solo elimina la asociación.
    # No elimina la regla ni el territorio.
    # ============================================================

    async def delete(
        self,
        promotion_rule_id: uuid.UUID,
        territory_id: uuid.UUID,
    ) -> None:

        rule_territory = (
            await self.repository.find_by_rule_and_territory(
                promotion_rule_id=promotion_rule_id,
                territory_id=territory_id,
            )
        )

        if rule_territory is None:
            raise LookupError(
                "El territorio no está asociado "
                "a esta regla promocional"
            )

        try:
            await self.repository.delete(
                rule_territory
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR EXISTENCIA DE REGLA
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
    # VALIDAR EXISTENCIA DEL TERRITORIO
    # ============================================================

    async def _validate_territory_exists(
        self,
        territory_id: uuid.UUID,
    ):
        territory = await self.territory_repository.find_by_id(
            territory_id
        )

        if territory is None:
            raise ValueError(
                "El territorio seleccionado no existe"
            )

        return territory

    # ============================================================
    # VALIDAR TERRITORIO ACTIVO
    # ============================================================

    async def _validate_active_territory(
        self,
        territory_id: uuid.UUID,
    ):
        territory = await self._validate_territory_exists(
            territory_id
        )

        if not territory.active:
            raise ValueError(
                "El territorio seleccionado está inactivo"
            )

        return territory
