import uuid
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.brands.model import Brand
from app.modules.colors.model import Color
from app.modules.motorcycles.model import MotorcycleModel
from app.modules.motorcycle_variants.model import (
    MotorcycleVariant,
)
from app.modules.territories.model import Territory

from app.modules.promotion_campaigns.model import (
    PromotionCampaign,
)
from app.modules.promotion_campaign_brands.model import (
    PromotionCampaignBrand,
)
from app.modules.promotion_documents.model import (
    PromotionDocument,
)
from app.modules.promotion_funding_sources.model import (
    PromotionFundingSource,
)
from app.modules.promotion_rules.model import (
    PromotionRule,
)
from app.modules.promotion_rule_colors.model import (
    PromotionRuleColor,
)
from app.modules.promotion_rule_funding.model import (
    PromotionRuleFunding,
)
from app.modules.promotion_rule_models.model import (
    PromotionRuleModel,
)
from app.modules.promotion_rule_territories.model import (
    PromotionRuleTerritory,
)
from app.modules.promotion_rule_variants.model import (
    PromotionRuleVariant,
)
from app.modules.promotion_rule_years.model import (
    PromotionRuleYear,
)


class PromotionRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ============================================================
    # LISTAR CAMPAÑAS
    #
    # Filtros:
    #
    # status
    # date_from
    # date_to
    # search
    #
    # Las fechas se manejan como rango de solapamiento.
    #
    # Ejemplo:
    #
    # date_from = 2026-09-01
    # date_to   = 2026-09-30
    #
    # devuelve campañas que estuvieron vigentes en algún punto
    # dentro de septiembre.
    # ============================================================

    async def find_all_campaigns(
        self,
        *,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
    ) -> list[PromotionCampaign]:

        query = select(
            PromotionCampaign
        )

        # ========================================================
        # STATUS
        # ========================================================

        if status is not None:
            query = query.where(
                PromotionCampaign.status == status
            )

        # ========================================================
        # FECHA DESDE
        #
        # La campaña debe terminar en o después de date_from.
        # ========================================================

        if date_from is not None:
            query = query.where(
                PromotionCampaign.end_date
                >= date_from
            )

        # ========================================================
        # FECHA HASTA
        #
        # La campaña debe iniciar en o antes de date_to.
        # ========================================================

        if date_to is not None:
            query = query.where(
                PromotionCampaign.start_date
                <= date_to
            )

        # ========================================================
        # BUSQUEDA
        #
        # Busca tanto en:
        #
        # name
        # description
        #
        # ILIKE = búsqueda case-insensitive en PostgreSQL.
        # ========================================================

        if search is not None:

            normalized_search = (
                search.strip()
            )

            if normalized_search:

                pattern = (
                    f"%{normalized_search}%"
                )

                query = query.where(
                    or_(
                        PromotionCampaign.name.ilike(
                            pattern
                        ),
                        PromotionCampaign.description.ilike(
                            pattern
                        ),
                    )
                )

        # ========================================================
        # ORDEN
        #
        # Primero las campañas más recientes.
        # ========================================================

        query = query.order_by(
            PromotionCampaign.start_date.desc(),
            PromotionCampaign.created_at.desc(),
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # CAMPAÑA
    # ============================================================

    async def find_campaign_by_id(
        self,
        campaign_id: uuid.UUID,
    ) -> PromotionCampaign | None:

        query = select(
            PromotionCampaign
        ).where(
            PromotionCampaign.id == campaign_id
        )

        result = await self.db.execute(
            query
        )

        return result.scalar_one_or_none()

    # ============================================================
    # MARCAS DE LA CAMPAÑA
    #
    # promotion_campaign_brands
    #              +
    # brands
    # ============================================================

    async def find_brands_by_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> list[Brand]:

        query = (
            select(Brand)
            .join(
                PromotionCampaignBrand,
                PromotionCampaignBrand.brand_id
                == Brand.id,
            )
            .where(
                PromotionCampaignBrand.campaign_id
                == campaign_id
            )
            .order_by(
                Brand.name.asc()
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # REGLAS DE LA CAMPAÑA
    # ============================================================

    async def find_rules_by_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> list[PromotionRule]:

        query = (
            select(PromotionRule)
            .where(
                PromotionRule.campaign_id
                == campaign_id
            )
            .order_by(
                PromotionRule.priority.asc(),
                PromotionRule.created_at.asc(),
                PromotionRule.id.asc(),
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # DOCUMENTOS DE LA CAMPAÑA
    # ============================================================

    async def find_documents_by_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> list[PromotionDocument]:

        query = (
            select(PromotionDocument)
            .where(
                PromotionDocument.campaign_id
                == campaign_id
            )
            .order_by(
                PromotionDocument.created_at.desc()
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # MODELOS DE TODAS LAS REGLAS
    #
    # Devuelve:
    #
    # promotion_rule_id
    # MotorcycleModel
    #
    # Así el service puede agruparlos posteriormente.
    # ============================================================

    async def find_models_by_rule_ids(
        self,
        rule_ids: list[uuid.UUID],
    ):

        if not rule_ids:
            return []

        query = (
            select(
                PromotionRuleModel.promotion_rule_id,
                MotorcycleModel,
            )
            .join(
                MotorcycleModel,
                MotorcycleModel.id
                == PromotionRuleModel.model_id,
            )
            .where(
                PromotionRuleModel.promotion_rule_id.in_(
                    rule_ids
                )
            )
            .order_by(
                PromotionRuleModel.promotion_rule_id.asc(),
                MotorcycleModel.name.asc(),
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.all()
        )

    # ============================================================
    # VARIANTES DE TODAS LAS REGLAS
    # ============================================================

    async def find_variants_by_rule_ids(
        self,
        rule_ids: list[uuid.UUID],
    ):

        if not rule_ids:
            return []

        query = (
            select(
                PromotionRuleVariant.promotion_rule_id,
                MotorcycleVariant,
            )
            .join(
                MotorcycleVariant,
                MotorcycleVariant.id
                == PromotionRuleVariant.variant_id,
            )
            .where(
                PromotionRuleVariant.promotion_rule_id.in_(
                    rule_ids
                )
            )
            .order_by(
                PromotionRuleVariant.promotion_rule_id.asc(),
                MotorcycleVariant.model_year.asc(),
                MotorcycleVariant.commercial_name.asc(),
                MotorcycleVariant.id.asc(),
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.all()
        )

    # ============================================================
    # AÑOS DE TODAS LAS REGLAS
    # ============================================================

    async def find_years_by_rule_ids(
        self,
        rule_ids: list[uuid.UUID],
    ):

        if not rule_ids:
            return []

        query = (
            select(
                PromotionRuleYear.promotion_rule_id,
                PromotionRuleYear.model_year,
            )
            .where(
                PromotionRuleYear.promotion_rule_id.in_(
                    rule_ids
                )
            )
            .order_by(
                PromotionRuleYear.promotion_rule_id.asc(),
                PromotionRuleYear.model_year.asc(),
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.all()
        )

    # ============================================================
    # COLORES DE TODAS LAS REGLAS
    # ============================================================

    async def find_colors_by_rule_ids(
        self,
        rule_ids: list[uuid.UUID],
    ):

        if not rule_ids:
            return []

        query = (
            select(
                PromotionRuleColor.promotion_rule_id,
                Color,
            )
            .join(
                Color,
                Color.id
                == PromotionRuleColor.color_id,
            )
            .where(
                PromotionRuleColor.promotion_rule_id.in_(
                    rule_ids
                )
            )
            .order_by(
                PromotionRuleColor.promotion_rule_id.asc(),
                Color.name.asc(),
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.all()
        )

    # ============================================================
    # TERRITORIOS DE TODAS LAS REGLAS
    # ============================================================

    async def find_territories_by_rule_ids(
        self,
        rule_ids: list[uuid.UUID],
    ):

        if not rule_ids:
            return []

        query = (
            select(
                PromotionRuleTerritory.promotion_rule_id,
                Territory,
            )
            .join(
                Territory,
                Territory.id
                == PromotionRuleTerritory.territory_id,
            )
            .where(
                PromotionRuleTerritory.promotion_rule_id.in_(
                    rule_ids
                )
            )
            .order_by(
                PromotionRuleTerritory.promotion_rule_id.asc(),
                Territory.name.asc(),
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.all()
        )

    # ============================================================
    # FUNDING DE TODAS LAS REGLAS
    #
    # Devuelve:
    #
    # promotion_rule_id
    # PromotionRuleFunding
    # PromotionFundingSource
    #
    # Necesitamos ambos porque:
    #
    # promotion_rule_funding
    # ├── amount
    # └── percentage
    #
    # promotion_funding_sources
    # ├── name
    # ├── code
    # └── active
    # ============================================================

    async def find_funding_by_rule_ids(
        self,
        rule_ids: list[uuid.UUID],
    ):

        if not rule_ids:
            return []

        query = (
            select(
                PromotionRuleFunding.promotion_rule_id,
                PromotionRuleFunding,
                PromotionFundingSource,
            )
            .join(
                PromotionFundingSource,
                PromotionFundingSource.id
                == PromotionRuleFunding.funding_source_id,
            )
            .where(
                PromotionRuleFunding.promotion_rule_id.in_(
                    rule_ids
                )
            )
            .order_by(
                PromotionRuleFunding.promotion_rule_id.asc(),
                PromotionFundingSource.name.asc(),
            )
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.all()
        )
