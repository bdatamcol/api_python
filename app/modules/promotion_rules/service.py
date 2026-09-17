import re
import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_campaigns.repository import (
    PromotionCampaignRepository,
)
from app.modules.promotion_rules.model import (
    PromotionRule,
)
from app.modules.promotion_rules.repository import (
    PromotionRuleRepository,
)
from app.modules.promotion_rules.schemas import (
    PromotionBenefitType,
    PromotionRuleCreateForCampaign,
    PromotionRuleUpdate,
)


class PromotionRuleService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionRuleRepository(db)

        self.campaign_repository = (
            PromotionCampaignRepository(db)
        )

    # ============================================================
    # LISTAR REGLAS
    # ============================================================

    async def find_all(
        self,
        campaign_id: uuid.UUID | None = None,
        active: bool | None = None,
        benefit_type: PromotionBenefitType | None = None,
    ) -> list[PromotionRule]:

        if campaign_id is not None:
            await self._validate_campaign_exists(
                campaign_id
            )

        benefit_type_value = (
            benefit_type.value
            if benefit_type is not None
            else None
        )

        return await self.repository.find_all(
            campaign_id=campaign_id,
            active=active,
            benefit_type=benefit_type_value,
        )

    # ============================================================
    # LISTAR REGLAS DE UNA CAMPAÑA
    # ============================================================

    async def find_all_by_campaign(
        self,
        campaign_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[PromotionRule]:

        await self._validate_campaign_exists(
            campaign_id
        )

        return await self.repository.find_all_by_campaign(
            campaign_id=campaign_id,
            active=active,
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        rule_id: uuid.UUID,
    ) -> PromotionRule:

        rule = await self.repository.find_by_id(
            rule_id
        )

        if rule is None:
            raise LookupError(
                "La regla promocional no existe"
            )

        return rule

    # ============================================================
    # CREAR REGLA DENTRO DE UNA CAMPAÑA
    # ============================================================

    async def create_for_campaign(
        self,
        campaign_id: uuid.UUID,
        data: PromotionRuleCreateForCampaign,
    ) -> PromotionRule:

        # ========================================================
        # VALIDAR CAMPAÑA
        # ========================================================

        await self._validate_campaign_exists(
            campaign_id
        )

        # ========================================================
        # NORMALIZAR TEXTOS
        # ========================================================

        name = self._clean_optional_text(
            data.name
        )

        gift_description = (
            self._clean_optional_text(
                data.gift_description
            )
        )

        terms = self._clean_optional_text(
            data.terms
        )

        # ========================================================
        # VALIDAR BENEFICIO
        #
        # Además devuelve solamente los campos que corresponden
        # al benefit_type.
        # ========================================================

        benefit_data = (
            self._prepare_benefit_data(
                benefit_type=data.benefit_type.value,
                benefit_amount=data.benefit_amount,
                benefit_percentage=data.benefit_percentage,
                gift_description=gift_description,
            )
        )

        try:
            rule = await self.repository.create(
                campaign_id=campaign_id,
                name=name,
                benefit_type=data.benefit_type.value,
                benefit_amount=(
                    benefit_data["benefit_amount"]
                ),
                benefit_percentage=(
                    benefit_data["benefit_percentage"]
                ),
                gift_description=(
                    benefit_data["gift_description"]
                ),
                terms=terms,
                priority=data.priority,
                active=data.active,
            )

            await self.db.commit()

            await self.db.refresh(
                rule
            )

            return rule

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR REGLA
    # ============================================================

    async def update(
        self,
        rule_id: uuid.UUID,
        data: PromotionRuleUpdate,
    ) -> PromotionRule:

        rule = await self.repository.find_by_id(
            rule_id
        )

        if rule is None:
            raise LookupError(
                "La regla promocional no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return rule

        # ========================================================
        # CAMPOS QUE NO PUEDEN QUEDAR NULL
        # ========================================================

        if (
            "benefit_type" in update_data
            and update_data["benefit_type"] is None
        ):
            raise ValueError(
                "El tipo de beneficio no puede ser nulo"
            )

        if (
            "priority" in update_data
            and update_data["priority"] is None
        ):
            raise ValueError(
                "La prioridad no puede ser nula"
            )

        if (
            "active" in update_data
            and update_data["active"] is None
        ):
            raise ValueError(
                "El estado activo no puede ser nulo"
            )

        # ========================================================
        # NORMALIZAR NOMBRE
        # ========================================================

        if "name" in update_data:
            update_data["name"] = (
                self._clean_optional_text(
                    update_data["name"]
                )
            )

        # ========================================================
        # NORMALIZAR TERMINOS
        # ========================================================

        if "terms" in update_data:
            update_data["terms"] = (
                self._clean_optional_text(
                    update_data["terms"]
                )
            )

        # ========================================================
        # NORMALIZAR DESCRIPCION DE OBSEQUIO
        # ========================================================

        if "gift_description" in update_data:
            update_data["gift_description"] = (
                self._clean_optional_text(
                    update_data["gift_description"]
                )
            )

        # ========================================================
        # CALCULAR TIPO FINAL
        # ========================================================

        final_benefit_type = update_data.get(
            "benefit_type",
            rule.benefit_type,
        )

        if isinstance(
            final_benefit_type,
            PromotionBenefitType,
        ):
            final_benefit_type = (
                final_benefit_type.value
            )

        # ========================================================
        # CALCULAR VALORES FINALES
        #
        # Si un campo no viene en el PATCH,
        # utilizamos el valor actual de PostgreSQL.
        # ========================================================

        final_benefit_amount = (
            update_data["benefit_amount"]
            if "benefit_amount" in update_data
            else rule.benefit_amount
        )

        final_benefit_percentage = (
            update_data["benefit_percentage"]
            if "benefit_percentage" in update_data
            else rule.benefit_percentage
        )

        final_gift_description = (
            update_data["gift_description"]
            if "gift_description" in update_data
            else rule.gift_description
        )

        # ========================================================
        # VALIDAR ESTADO FINAL DEL BENEFICIO
        #
        # También limpia automáticamente campos incompatibles.
        # ========================================================

        benefit_data = (
            self._prepare_benefit_data(
                benefit_type=final_benefit_type,
                benefit_amount=final_benefit_amount,
                benefit_percentage=(
                    final_benefit_percentage
                ),
                gift_description=(
                    final_gift_description
                ),
            )
        )

        update_data["benefit_type"] = (
            final_benefit_type
        )

        update_data["benefit_amount"] = (
            benefit_data["benefit_amount"]
        )

        update_data["benefit_percentage"] = (
            benefit_data["benefit_percentage"]
        )

        update_data["gift_description"] = (
            benefit_data["gift_description"]
        )

        try:
            rule = await self.repository.update(
                rule=rule,
                data=update_data,
            )

            await self.db.commit()

            await self.db.refresh(
                rule
            )

            return rule

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar la regla promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR REGLA
    #
    # No hacemos DELETE físico.
    # ============================================================

    async def deactivate(
        self,
        rule_id: uuid.UUID,
    ) -> PromotionRule:

        rule = await self.repository.find_by_id(
            rule_id
        )

        if rule is None:
            raise LookupError(
                "La regla promocional no existe"
            )

        if not rule.active:
            return rule

        try:
            rule = await self.repository.update(
                rule=rule,
                data={
                    "active": False,
                },
            )

            await self.db.commit()

            await self.db.refresh(
                rule
            )

            return rule

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR CAMPAÑA
    # ============================================================

    async def _validate_campaign_exists(
        self,
        campaign_id: uuid.UUID,
    ):
        campaign = (
            await self.campaign_repository.find_by_id(
                campaign_id
            )
        )

        if campaign is None:
            raise ValueError(
                "La campaña promocional seleccionada no existe"
            )

        return campaign

    # ============================================================
    # PREPARAR Y VALIDAR BENEFICIO
    #
    # Mantiene exactamente un tipo de valor coherente
    # con benefit_type.
    # ============================================================

    @staticmethod
    def _prepare_benefit_data(
        benefit_type: str,
        benefit_amount: int | None,
        benefit_percentage: Decimal | None,
        gift_description: str | None,
    ) -> dict:

        # ========================================================
        # FIXED_DISCOUNT / BONUS / CASHBACK
        # ========================================================

        if benefit_type in {
            PromotionBenefitType.FIXED_DISCOUNT.value,
            PromotionBenefitType.BONUS.value,
            PromotionBenefitType.CASHBACK.value,
        }:

            if benefit_amount is None:
                raise ValueError(
                    f"{benefit_type} requiere benefit_amount"
                )

            if benefit_amount < 0:
                raise ValueError(
                    "El monto del beneficio no puede ser negativo"
                )

            return {
                "benefit_amount": benefit_amount,
                "benefit_percentage": None,
                "gift_description": None,
            }

        # ========================================================
        # PERCENTAGE_DISCOUNT
        # ========================================================

        if (
            benefit_type
            == PromotionBenefitType
            .PERCENTAGE_DISCOUNT
            .value
        ):

            if benefit_percentage is None:
                raise ValueError(
                    "PERCENTAGE_DISCOUNT requiere benefit_percentage"
                )

            if (
                benefit_percentage < 0
                or benefit_percentage > 100
            ):
                raise ValueError(
                    "El porcentaje debe estar entre 0 y 100"
                )

            return {
                "benefit_amount": None,
                "benefit_percentage": benefit_percentage,
                "gift_description": None,
            }

        # ========================================================
        # GIFT
        # ========================================================

        if (
            benefit_type
            == PromotionBenefitType.GIFT.value
        ):

            if (
                gift_description is None
                or not gift_description.strip()
            ):
                raise ValueError(
                    "GIFT requiere gift_description"
                )

            return {
                "benefit_amount": None,
                "benefit_percentage": None,
                "gift_description": gift_description,
            }

        raise ValueError(
            f"Tipo de beneficio no soportado: {benefit_type}"
        )

    # ============================================================
    # LIMPIAR TEXTO OPCIONAL
    # ============================================================

    @staticmethod
    def _clean_optional_text(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value or None