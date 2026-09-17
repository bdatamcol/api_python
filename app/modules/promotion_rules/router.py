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
from app.modules.promotion_rules.schemas import (
    PromotionBenefitType,
    PromotionRuleCreateForCampaign,
    PromotionRuleResponse,
    PromotionRuleUpdate,
)
from app.modules.promotion_rules.service import (
    PromotionRuleService,
)


router = APIRouter(
    tags=["Admin - Promotion Rules"],
)


# ============================================================
# LISTAR TODAS LAS REGLAS
#
# Filtros opcionales:
#
# campaign_id
# active
# benefit_type
# ============================================================

@router.get(
    "/promotion-rules",
    response_model=list[PromotionRuleResponse],
    status_code=status.HTTP_200_OK,
)
async def list_promotion_rules(
    campaign_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar por campaña",
    ),
    active: bool | None = Query(
        default=None,
        description="Filtrar reglas activas o inactivas",
    ),
    benefit_type: PromotionBenefitType | None = Query(
        default=None,
        description="Filtrar por tipo de beneficio",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleService(db)

    try:
        return await service.find_all(
            campaign_id=campaign_id,
            active=active,
            benefit_type=benefit_type,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# LISTAR REGLAS DE UNA CAMPAÑA
# ============================================================

@router.get(
    "/promotion-campaigns/{campaign_id}/rules",
    response_model=list[PromotionRuleResponse],
    status_code=status.HTTP_200_OK,
)
async def list_campaign_rules(
    campaign_id: uuid.UUID,
    active: bool | None = Query(
        default=None,
        description="Filtrar reglas activas o inactivas",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleService(db)

    try:
        return await service.find_all_by_campaign(
            campaign_id=campaign_id,
            active=active,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR REGLA PARA UNA CAMPAÑA
# ============================================================

@router.post(
    "/promotion-campaigns/{campaign_id}/rules",
    response_model=PromotionRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign_rule(
    campaign_id: uuid.UUID,
    data: PromotionRuleCreateForCampaign,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleService(db)

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
# OBTENER REGLA POR ID
# ============================================================

@router.get(
    "/promotion-rules/{rule_id}",
    response_model=PromotionRuleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_promotion_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleService(db)

    try:
        return await service.find_by_id(
            rule_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR REGLA
# ============================================================

@router.patch(
    "/promotion-rules/{rule_id}",
    response_model=PromotionRuleResponse,
    status_code=status.HTTP_200_OK,
)
async def update_promotion_rule(
    rule_id: uuid.UUID,
    data: PromotionRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleService(db)

    try:
        return await service.update(
            rule_id=rule_id,
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
# DESACTIVAR REGLA
#
# No se elimina físicamente.
#
# active = false
# ============================================================

@router.delete(
    "/promotion-rules/{rule_id}",
    response_model=PromotionRuleResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_promotion_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleService(db)

    try:
        return await service.deactivate(
            rule_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc