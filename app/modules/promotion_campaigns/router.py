import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.promotion_campaigns.schemas import (
    PromotionCampaignCreate,
    PromotionCampaignResponse,
    PromotionCampaignStatus,
    PromotionCampaignUpdate,
)
from app.modules.promotion_campaigns.service import (
    PromotionCampaignService,
)


router = APIRouter(
    prefix="/promotion-campaigns",
    tags=["Admin - Promotion Campaigns"],
)


# ============================================================
# LISTAR CAMPAÑAS
# ============================================================

@router.get(
    "",
    response_model=list[PromotionCampaignResponse],
    status_code=status.HTTP_200_OK,
)
async def list_promotion_campaigns(
    campaign_status: PromotionCampaignStatus | None = Query(
        default=None,
        alias="status",
        description="Filtrar campañas por estado",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignService(db)

    return await service.find_all(
        status=campaign_status
    )


# ============================================================
# OBTENER CAMPAÑA POR ID
# ============================================================

@router.get(
    "/{campaign_id}",
    response_model=PromotionCampaignResponse,
    status_code=status.HTTP_200_OK,
)
async def get_promotion_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignService(db)

    try:
        return await service.find_by_id(
            campaign_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR CAMPAÑA
# ============================================================

@router.post(
    "",
    response_model=PromotionCampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_promotion_campaign(
    data: PromotionCampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignService(db)

    try:
        return await service.create(
            data
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR CAMPAÑA
# ============================================================

@router.patch(
    "/{campaign_id}",
    response_model=PromotionCampaignResponse,
    status_code=status.HTTP_200_OK,
)
async def update_promotion_campaign(
    campaign_id: uuid.UUID,
    data: PromotionCampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignService(db)

    try:
        return await service.update(
            campaign_id=campaign_id,
            data=data,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CANCELAR CAMPAÑA
#
# No elimina físicamente.
#
# status = CANCELLED
# ============================================================

@router.delete(
    "/{campaign_id}",
    response_model=PromotionCampaignResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_promotion_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionCampaignService(db)

    try:
        return await service.cancel(
            campaign_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc