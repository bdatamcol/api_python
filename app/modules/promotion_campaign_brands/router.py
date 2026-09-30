import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.promotion_campaign_brands.schemas import (
    PromotionCampaignBrandCreateForCampaign,
    PromotionCampaignBrandResponse,
)
from app.modules.promotion_campaign_brands.service import (
    PromotionCampaignBrandService,
)


router = APIRouter(
    tags=["Admin - Promotion Campaign Brands"],
)


# ============================================================
# LISTAR MARCAS DE UNA CAMPAÑA
# ============================================================

@router.get(
    "/promotion-campaigns/{campaign_id}/brands",
    response_model=list[PromotionCampaignBrandResponse],
    status_code=status.HTTP_200_OK,
)
async def list_campaign_brands(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignBrandService(db)

    try:
        return await service.find_all_by_campaign(
            campaign_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# AGREGAR MARCA A UNA CAMPAÑA
# ============================================================

@router.post(
    "/promotion-campaigns/{campaign_id}/brands",
    response_model=PromotionCampaignBrandResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_brand_to_campaign(
    campaign_id: uuid.UUID,
    data: PromotionCampaignBrandCreateForCampaign,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignBrandService(db)

    try:
        return await service.create_for_campaign(
            campaign_id=campaign_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# QUITAR MARCA DE UNA CAMPAÑA
# ============================================================

@router.delete(
    "/promotion-campaigns/{campaign_id}/brands/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_brand_from_campaign(
    campaign_id: uuid.UUID,
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignBrandService(db)

    try:
        await service.delete(
            campaign_id=campaign_id,
            brand_id=brand_id,
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# LISTAR CAMPAÑAS ASOCIADAS A UNA MARCA
# ============================================================

@router.get(
    "/brands/{brand_id}/promotion-campaigns",
    response_model=list[PromotionCampaignBrandResponse],
    status_code=status.HTTP_200_OK,
)
async def list_brand_campaigns(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignBrandService(db)

    try:
        return await service.find_all_by_brand(
            brand_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc