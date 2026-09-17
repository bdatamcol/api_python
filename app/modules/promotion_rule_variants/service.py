import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motorcycle_variants.repository import (
    MotorcycleVariantRepository,
)
from app.modules.promotion_rule_variants.model import (
    PromotionRuleVariant,
)
from app.modules.promotion_rule_variants.repository import (
    PromotionRuleVariantRepository,
)
from app.modules.promotion_rule_variants.schemas import (
    PromotionRuleVariantCreateForRule,
)
from app.modules.promotion_rules.repository import (
    PromotionRuleRepository,
)


class PromotionRuleVariantService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionRuleVariantRepository(db)

        self.rule_repository = PromotionRuleRepository(db)

        self.variant_repository = MotorcycleVariantRepository(db)

    # ============================================================
    # LISTAR VARIANTES DE UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleVariant]:

        await self._validate_rule_exists(
            promotion_rule_id
        )

        return await self.repository.find_all_by_rule(
            promotion_rule_id
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UNA VARIANTE
    # ============================================================

    async def find_all_by_variant(
        self,
        variant_id: uuid.UUID,
    ) -> list[PromotionRuleVariant]:

        await self._validate_variant_exists(
            variant_id
        )

        return await self.repository.find_all_by_variant(
            variant_id
        )

    # ============================================================
    # ASOCIAR VARIANTE A UNA REGLA
    # ============================================================

    async def create_for_rule(
        self,
        promotion_rule_id: uuid.UUID,
        data: PromotionRuleVariantCreateForRule,
    ) -> PromotionRuleVariant:

        # ========================================================
        # VALIDAR REGLA ACTIVA
        # ========================================================

        await self._validate_active_rule(
            promotion_rule_id
        )

        # ========================================================
        # VALIDAR VARIANTE ACTIVA
        # ========================================================

        await self._validate_active_variant(
            data.variant_id
        )

        # ========================================================
        # EVITAR DUPLICADOS
        #
        # promotion_rule_id + variant_id
        # es la PK compuesta en PostgreSQL.
        # ========================================================

        existing_relation = (
            await self.repository.find_by_rule_and_variant(
                promotion_rule_id=promotion_rule_id,
                variant_id=data.variant_id,
            )
        )

        if existing_relation is not None:
            raise ValueError(
                "La variante ya está asociada a esta regla promocional"
            )

        try:
            rule_variant = await self.repository.create(
                promotion_rule_id=promotion_rule_id,
                variant_id=data.variant_id,
            )

            await self.db.commit()

            await self.db.refresh(
                rule_variant
            )

            return rule_variant

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible asociar la variante a la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR ASOCIACION
    #
    # Solamente elimina:
    #
    # promotion_rule_id + variant_id
    #
    # No elimina ni la regla ni la variante.
    # ============================================================

    async def delete(
        self,
        promotion_rule_id: uuid.UUID,
        variant_id: uuid.UUID,
    ) -> None:

        rule_variant = (
            await self.repository.find_by_rule_and_variant(
                promotion_rule_id=promotion_rule_id,
                variant_id=variant_id,
            )
        )

        if rule_variant is None:
            raise LookupError(
                "La variante no está asociada a esta regla promocional"
            )

        try:
            await self.repository.delete(
                rule_variant
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
    # VALIDAR VARIANTE
    # ============================================================

    async def _validate_variant_exists(
        self,
        variant_id: uuid.UUID,
    ):
        variant = await self.variant_repository.find_by_id(
            variant_id
        )

        if variant is None:
            raise ValueError(
                "La variante seleccionada no existe"
            )

        return variant

    # ============================================================
    # VALIDAR VARIANTE ACTIVA
    # ============================================================

    async def _validate_active_variant(
        self,
        variant_id: uuid.UUID,
    ):
        variant = await self._validate_variant_exists(
            variant_id
        )

        if not variant.active:
            raise ValueError(
                "La variante seleccionada está inactiva"
            )

        return variant