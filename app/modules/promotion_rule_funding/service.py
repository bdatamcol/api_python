import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_funding_sources.repository import (
    PromotionFundingSourceRepository,
)
from app.modules.promotion_rule_funding.model import (
    PromotionRuleFunding,
)
from app.modules.promotion_rule_funding.repository import (
    PromotionRuleFundingRepository,
)
from app.modules.promotion_rule_funding.schemas import (
    PromotionRuleFundingCreateForRule,
    PromotionRuleFundingUpdate,
)
from app.modules.promotion_rules.repository import (
    PromotionRuleRepository,
)


class PromotionRuleFundingService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionRuleFundingRepository(db)

        self.rule_repository = PromotionRuleRepository(db)

        self.funding_source_repository = (
            PromotionFundingSourceRepository(db)
        )

    # ============================================================
    # LISTAR FUENTES DE FINANCIACION DE UNA REGLA
    # ============================================================

    async def find_all_by_rule(
        self,
        promotion_rule_id: uuid.UUID,
    ) -> list[PromotionRuleFunding]:

        await self._validate_rule_exists(
            promotion_rule_id
        )

        return await self.repository.find_all_by_rule(
            promotion_rule_id
        )

    # ============================================================
    # LISTAR REGLAS ASOCIADAS A UNA FUENTE
    # ============================================================

    async def find_all_by_funding_source(
        self,
        funding_source_id: uuid.UUID,
    ) -> list[PromotionRuleFunding]:

        await self._validate_funding_source_exists(
            funding_source_id
        )

        return await self.repository.find_all_by_funding_source(
            funding_source_id
        )

    # ============================================================
    # ASOCIAR FUENTE A UNA REGLA
    # ============================================================

    async def create_for_rule(
        self,
        promotion_rule_id: uuid.UUID,
        data: PromotionRuleFundingCreateForRule,
    ) -> PromotionRuleFunding:

        # ========================================================
        # VALIDAR REGLA ACTIVA
        # ========================================================

        await self._validate_active_rule(
            promotion_rule_id
        )

        # ========================================================
        # VALIDAR FUENTE ACTIVA
        # ========================================================

        await self._validate_active_funding_source(
            data.funding_source_id
        )

        # ========================================================
        # VALIDAR VALORES
        # ========================================================

        self._validate_values(
            amount=data.amount,
            percentage=data.percentage,
        )

        # ========================================================
        # EVITAR DUPLICADOS
        #
        # promotion_rule_id + funding_source_id
        # es la PK compuesta.
        # ========================================================

        existing_relation = (
            await self.repository.find_by_rule_and_funding_source(
                promotion_rule_id=promotion_rule_id,
                funding_source_id=data.funding_source_id,
            )
        )

        if existing_relation is not None:
            raise ValueError(
                "La fuente de financiación ya está asociada "
                "a esta regla promocional"
            )

        try:
            rule_funding = await self.repository.create(
                promotion_rule_id=promotion_rule_id,
                funding_source_id=data.funding_source_id,
                amount=data.amount,
                percentage=data.percentage,
            )

            await self.db.commit()

            await self.db.refresh(
                rule_funding
            )

            return rule_funding

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible asociar la fuente de financiación "
                "a la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR APORTE DE UNA FUENTE
    # ============================================================

    async def update(
        self,
        promotion_rule_id: uuid.UUID,
        funding_source_id: uuid.UUID,
        data: PromotionRuleFundingUpdate,
    ) -> PromotionRuleFunding:

        # ========================================================
        # VALIDAR QUE LA RELACION EXISTA
        # ========================================================

        rule_funding = (
            await self.repository.find_by_rule_and_funding_source(
                promotion_rule_id=promotion_rule_id,
                funding_source_id=funding_source_id,
            )
        )

        if rule_funding is None:
            raise LookupError(
                "La fuente de financiación no está asociada "
                "a esta regla promocional"
            )

        # ========================================================
        # NO PERMITIR MODIFICAR UNA REGLA INACTIVA
        # ========================================================

        await self._validate_active_rule(
            promotion_rule_id
        )

        # ========================================================
        # NO PERMITIR MODIFICAR UNA FUENTE INACTIVA
        # ========================================================

        await self._validate_active_funding_source(
            funding_source_id
        )

        # ========================================================
        # VALIDAR QUE EL PATCH TENGA ALGO
        #
        # model_fields_set permite distinguir:
        #
        # {}
        #
        # de:
        #
        # {"amount": null}
        # ========================================================

        fields_set = data.model_fields_set

        if not fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar"
            )

        # ========================================================
        # CONSERVAR CAMPOS NO ENVIADOS
        # ========================================================

        new_amount = (
            data.amount
            if "amount" in fields_set
            else rule_funding.amount
        )

        new_percentage = (
            data.percentage
            if "percentage" in fields_set
            else rule_funding.percentage
        )

        # ========================================================
        # VALIDAR RESULTADO FINAL
        #
        # Nunca pueden quedar ambos en NULL.
        # ========================================================

        self._validate_values(
            amount=new_amount,
            percentage=new_percentage,
        )

        try:
            updated = await self.repository.update(
                rule_funding,
                amount=new_amount,
                percentage=new_percentage,
            )

            await self.db.commit()

            await self.db.refresh(
                updated
            )

            return updated

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar el aporte "
                "de la fuente de financiación"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR FUENTE DE UNA REGLA
    # ============================================================

    async def delete(
        self,
        promotion_rule_id: uuid.UUID,
        funding_source_id: uuid.UUID,
    ) -> None:

        rule_funding = (
            await self.repository.find_by_rule_and_funding_source(
                promotion_rule_id=promotion_rule_id,
                funding_source_id=funding_source_id,
            )
        )

        if rule_funding is None:
            raise LookupError(
                "La fuente de financiación no está asociada "
                "a esta regla promocional"
            )

        try:
            await self.repository.delete(
                rule_funding
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
    # VALIDAR EXISTENCIA DE FUENTE
    # ============================================================

    async def _validate_funding_source_exists(
        self,
        funding_source_id: uuid.UUID,
    ):
        funding_source = (
            await self.funding_source_repository.find_by_id(
                funding_source_id
            )
        )

        if funding_source is None:
            raise ValueError(
                "La fuente de financiación seleccionada no existe"
            )

        return funding_source

    # ============================================================
    # VALIDAR FUENTE ACTIVA
    # ============================================================

    async def _validate_active_funding_source(
        self,
        funding_source_id: uuid.UUID,
    ):
        funding_source = (
            await self._validate_funding_source_exists(
                funding_source_id
            )
        )

        if not funding_source.active:
            raise ValueError(
                "La fuente de financiación seleccionada está inactiva"
            )

        return funding_source

    # ============================================================
    # VALIDAR VALORES DE APORTE
    #
    # Coincide con los CHECK de PostgreSQL.
    # ============================================================

    @staticmethod
    def _validate_values(
        amount: int | None,
        percentage: Decimal | None,
    ) -> None:

        if (
            amount is None
            and percentage is None
        ):
            raise ValueError(
                "Debe especificar amount, percentage o ambos"
            )

        if amount is not None and amount < 0:
            raise ValueError(
                "El monto no puede ser negativo"
            )

        if percentage is not None:
            if (
                percentage < Decimal("0")
                or percentage > Decimal("100")
            ):
                raise ValueError(
                    "El porcentaje debe estar entre 0 y 100"
                )
