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
from app.modules.promotion_rule_territories.schemas import (
    PromotionRuleTerritoryCreateForRule,
    PromotionRuleTerritoryResponse,
)
from app.modules.promotion_rule_territories.service import (
    PromotionRuleTerritoryService,
)


router = APIRouter(
    tags=["Admin - Promotion Rule Territories"],
)


# ============================================================
# LISTAR TERRITORIOS ASOCIADOS A UNA REGLA
# ============================================================

@router.get(
    "/promotion-rules/{rule_id}/territories",
    response_model=list[PromotionRuleTerritoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_rule_territories(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleTerritoryService(db)

    try:
        return await service.find_all_by_rule(
            rule_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# ASOCIAR TERRITORIO A UNA REGLA
# ============================================================

@router.post(
    "/promotion-rules/{rule_id}/territories",
    response_model=PromotionRuleTerritoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_territory_to_rule(
    rule_id: uuid.UUID,
    data: PromotionRuleTerritoryCreateForRule,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleTerritoryService(db)

    try:
        return await service.create_for_rule(
            promotion_rule_id=rule_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# ELIMINAR TERRITORIO DE UNA REGLA
# ============================================================

@router.delete(
    "/promotion-rules/{rule_id}/territories/{territory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_territory_from_rule(
    rule_id: uuid.UUID,
    territory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleTerritoryService(db)

    try:
        await service.delete(
            promotion_rule_id=rule_id,
            territory_id=territory_id,
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
# LISTAR REGLAS ASOCIADAS A UN TERRITORIO
# ============================================================

@router.get(
    "/territories/{territory_id}/promotion-rules",
    response_model=list[PromotionRuleTerritoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_territory_promotion_rules(
    territory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleTerritoryService(db)

    try:
        return await service.find_all_by_territory(
            territory_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
