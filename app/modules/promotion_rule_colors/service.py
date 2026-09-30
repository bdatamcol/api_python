import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.colors.repository import ColorRepository
from app.modules.promotion_rule_colors.model import (
    PromotionRuleColor,
)
from app.modules.promotion_rule_colors.repository import (
    PromotionRuleColorRepository,
)
from app.modules.promotion_rule_colors.schemas import (
    PromotionRuleColorCreateForRule,
)
from app.modules.promotion_rules.repository import (
    PromotionRuleRepository,
)


class PromotionRuleColorService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionRuleColorRepository(db)
        self.rule_repository = PromotionRuleRepository(db)
        self.color_repository = ColorRepository(db)

    # ============================================================
    # LISTAR COLORES DE UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleColor]:

        await self._validate_rule_exists(
            promotion_rule_id
        )

        return await self.repository.find_all_by_rule(
            promotion_rule_id
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UN COLOR
    # ============================================================

    async def find_all_by_color(
        self,
        color_id: uuid.UUID,
    ) -> list[PromotionRuleColor]:

        await self._validate_color_exists(
            color_id
        )

        return await self.repository.find_all_by_color(
            color_id
        )

    # ============================================================
    # ASOCIAR COLOR A UNA REGLA
    # ============================================================

    async def create_for_rule(
        self,
        promotion_rule_id: uuid.UUID,
        data: PromotionRuleColorCreateForRule,
    ) -> PromotionRuleColor:

        # ========================================================
        # VALIDAR REGLA ACTIVA
        # ========================================================

        await self._validate_active_rule(
            promotion_rule_id
        )

        # ========================================================
        # VALIDAR COLOR ACTIVO
        # ========================================================

        await self._validate_active_color(
            data.color_id
        )

        # ========================================================
        # EVITAR DUPLICADOS
        #
        # promotion_rule_id + color_id
        # es la PK compuesta.
        # ========================================================

        existing_relation = (
            await self.repository.find_by_rule_and_color(
                promotion_rule_id=promotion_rule_id,
                color_id=data.color_id,
            )
        )

        if existing_relation is not None:
            raise ValueError(
                "El color ya está asociado a esta regla promocional"
            )

        try:
            rule_color = await self.repository.create(
                promotion_rule_id=promotion_rule_id,
                color_id=data.color_id,
            )

            await self.db.commit()

            await self.db.refresh(
                rule_color
            )

            return rule_color

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible asociar el color a la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR COLOR DE UNA REGLA
    #
    # Solo elimina la asociación.
    # No elimina el color ni la regla.
    # ============================================================

    async def delete(
        self,
        promotion_rule_id: uuid.UUID,
        color_id: uuid.UUID,
    ) -> None:

        rule_color = (
            await self.repository.find_by_rule_and_color(
                promotion_rule_id=promotion_rule_id,
                color_id=color_id,
            )
        )

        if rule_color is None:
            raise LookupError(
                "El color no está asociado a esta regla promocional"
            )

        try:
            await self.repository.delete(
                rule_color
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
    # VALIDAR EXISTENCIA DEL COLOR
    # ============================================================

    async def _validate_color_exists(
        self,
        color_id: uuid.UUID,
    ):
        color = await self.color_repository.find_by_id(
            color_id
        )

        if color is None:
            raise ValueError(
                "El color seleccionado no existe"
            )

        return color

    # ============================================================
    # VALIDAR COLOR ACTIVO
    # ============================================================

    async def _validate_active_color(
        self,
        color_id: uuid.UUID,
    ):
        color = await self._validate_color_exists(
            color_id
        )

        if not color.active:
            raise ValueError(
                "El color seleccionado está inactivo"
            )

        return color