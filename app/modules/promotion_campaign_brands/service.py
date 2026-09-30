import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.brands.repository import BrandRepository
from app.modules.promotion_campaign_brands.model import (
    PromotionCampaignBrand,
)
from app.modules.promotion_campaign_brands.repository import (
    PromotionCampaignBrandRepository,
)
from app.modules.promotion_campaign_brands.schemas import (
    PromotionCampaignBrandCreateForCampaign,
)
from app.modules.promotion_campaigns.repository import (
    PromotionCampaignRepository,
)


class PromotionCampaignBrandService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionCampaignBrandRepository(db)

        self.campaign_repository = PromotionCampaignRepository(db)

        self.brand_repository = BrandRepository(db)

    # ============================================================
    # LISTAR MARCAS DE UNA CAMPAÑA
    # ============================================================

    async def find_all_by_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> list[PromotionCampaignBrand]:

        await self._validate_campaign_exists(
            campaign_id
        )

        return await self.repository.find_all_by_campaign(
            campaign_id
        )

    # ============================================================
    # LISTAR CAMPAÑAS DE UNA MARCA
    # ============================================================

    async def find_all_by_brand(
        self,
        brand_id: uuid.UUID,
    ) -> list[PromotionCampaignBrand]:

        await self._validate_brand_exists(
            brand_id
        )

        return await self.repository.find_all_by_brand(
            brand_id
        )

    # ============================================================
    # AGREGAR MARCA A UNA CAMPAÑA
    # ============================================================

    async def create_for_campaign(
        self,
        campaign_id: uuid.UUID,
        data: PromotionCampaignBrandCreateForCampaign,
    ) -> PromotionCampaignBrand:

        # ========================================================
        # VALIDAR CAMPAÑA
        # ========================================================

        await self._validate_campaign_exists(
            campaign_id
        )

        # ========================================================
        # VALIDAR MARCA ACTIVA
        # ========================================================

        await self._validate_active_brand(
            data.brand_id
        )

        # ========================================================
        # EVITAR DUPLICADOS
        #
        # campaign_id + brand_id es PK en PostgreSQL
        # ========================================================

        existing_relation = (
            await self.repository.find_by_campaign_and_brand(
                campaign_id=campaign_id,
                brand_id=data.brand_id,
            )
        )

        if existing_relation is not None:
            raise ValueError(
                "La marca ya está asociada a esta campaña"
            )

        try:
            campaign_brand = await self.repository.create(
                campaign_id=campaign_id,
                brand_id=data.brand_id,
            )

            await self.db.commit()

            await self.db.refresh(
                campaign_brand
            )

            return campaign_brand

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible asociar la marca a la campaña"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR MARCA DE UNA CAMPAÑA
    # ============================================================

    async def delete(
        self,
        campaign_id: uuid.UUID,
        brand_id: uuid.UUID,
    ) -> None:

        campaign_brand = (
            await self.repository.find_by_campaign_and_brand(
                campaign_id=campaign_id,
                brand_id=brand_id,
            )
        )

        if campaign_brand is None:
            raise LookupError(
                "La marca no está asociada a esta campaña"
            )

        try:
            await self.repository.delete(
                campaign_brand
            )

            await self.db.commit()

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
        campaign = await self.campaign_repository.find_by_id(
            campaign_id
        )

        if campaign is None:
            raise ValueError(
                "La campaña promocional seleccionada no existe"
            )

        return campaign

    # ============================================================
    # VALIDAR MARCA
    # ============================================================

    async def _validate_brand_exists(
        self,
        brand_id: uuid.UUID,
    ):
        brand = await self.brand_repository.find_by_id(
            brand_id
        )

        if brand is None:
            raise ValueError(
                "La marca seleccionada no existe"
            )

        return brand

    # ============================================================
    # VALIDAR MARCA ACTIVA
    # ============================================================

    async def _validate_active_brand(
        self,
        brand_id: uuid.UUID,
    ):
        brand = await self._validate_brand_exists(
            brand_id
        )

        if not brand.active:
            raise ValueError(
                "La marca seleccionada está inactiva"
            )

        return brand