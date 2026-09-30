import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.promotions.schemas import (
    PromotionCreateRequest,
    PromotionCreateResponse,
    PromotionDetailResponse,
)
from app.modules.promotions.service import (
    PromotionService,
)


router = APIRouter(
    prefix="/promotions",
    tags=["Admin - Promotions"],
)


# ============================================================
# CREAR PROMOCION COMPLETA
#
# Este endpoint crea en una sola operación:
#
# promotion_campaigns
# promotion_campaign_brands
# promotion_rules
# promotion_rule_models
# promotion_rule_variants
# promotion_rule_years
# promotion_rule_colors
# promotion_rule_territories
# promotion_rule_funding
# promotion_documents
#
# Todo dentro de una única transacción.
# ============================================================

@router.post(
    "",
    response_model=PromotionCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_promotion(
    data: PromotionCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionService(db)

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
# OBTENER PROMOCION COMPLETA POR ID
#
# Devuelve en una sola respuesta:
#
# campaign
# brands
# rules
#   ├── models
#   ├── variants
#   ├── years
#   ├── colors
#   ├── territories
#   └── funding
#
# documents
# ============================================================

@router.get(
    "/{campaign_id}",
    response_model=PromotionDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_promotion(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionService(db)

    try:
        return await service.find_by_id(
            campaign_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
