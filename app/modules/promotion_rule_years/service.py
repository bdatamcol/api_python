import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_rule_years.model import (
    PromotionRuleYear,
)
from app.modules.promotion_rule_years.repository import (
    PromotionRuleYearRepository,
)
from app.modules.promotion_rule_years.schemas import (
    PromotionRuleYearCreateForRule,
)
from app.modules.promotion_rules.repository import (
    PromotionRuleRepository,
)


class PromotionRuleYearService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionRuleYearRepository(db)

        self.rule_repository = PromotionRuleRepository(db)

    # ============================================================
    # LISTAR AÑOS DE UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleYear]:

        await self._validate_rule_exists(
            promotion_rule_id
        )

        return await self.repository.find_all_by_rule(
            promotion_rule_id
        )

    # ============================================================
    # ASOCIAR AÑO A UNA REGLA
    # ============================================================

    async def create_for_rule(
        self,
        promotion_rule_id: uuid.UUID,
        data: PromotionRuleYearCreateForRule,
    ) -> PromotionRuleYear:

        # ========================================================
        # VALIDAR REGLA ACTIVA
        # ========================================================

        await self._validate_active_rule(
            promotion_rule_id
        )

        # ========================================================
        # VALIDAR AÑO
        #
        # Pydantic ya lo valida, pero dejamos la protección
        # también en el service.
        # ========================================================

        self._validate_model_year(
            data.model_year
        )

        # ========================================================
        # EVITAR DUPLICADOS
        #
        # promotion_rule_id + model_year
        # es PK compuesta en PostgreSQL.
        # ========================================================

        existing_relation = (
            await self.repository.find_by_rule_and_year(
                promotion_rule_id=promotion_rule_id,
                model_year=data.model_year,
            )
        )

        if existing_relation is not None:
            raise ValueError(
                "El año ya está asociado a esta regla promocional"
            )

        try:
            rule_year = await self.repository.create(
                promotion_rule_id=promotion_rule_id,
                model_year=data.model_year,
            )

            await self.db.commit()

            await self.db.refresh(
                rule_year
            )

            return rule_year

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible asociar el año a la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR AÑO DE UNA REGLA
    #
    # Solamente eliminamos la asociación.
    # No eliminamos la regla promocional.
    # ============================================================

    async def delete(
        self,
        promotion_rule_id: uuid.UUID,
        model_year: int,
    ) -> None:

        self._validate_model_year(
            model_year
        )

        rule_year = (
            await self.repository.find_by_rule_and_year(
                promotion_rule_id=promotion_rule_id,
                model_year=model_year,
            )
        )

        if rule_year is None:
            raise LookupError(
                "El año no está asociado a esta regla promocional"
            )

        try:
            await self.repository.delete(
                rule_year
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
    # VALIDAR AÑO MODELO
    #
    # Debe coincidir con el CHECK de PostgreSQL:
    #
    # 1990 - 2100
    # ============================================================

    @staticmethod
    def _validate_model_year(
        model_year: int,
    ) -> None:

        if model_year < 1990 or model_year > 2100:
            raise ValueError(
                "El año modelo debe estar entre 1990 y 2100"
            )