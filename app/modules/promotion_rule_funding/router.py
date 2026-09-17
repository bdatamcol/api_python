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
from app.modules.promotion_rule_funding.schemas import (
    PromotionRuleFundingCreateForRule,
    PromotionRuleFundingResponse,
    PromotionRuleFundingUpdate,
)
from app.modules.promotion_rule_funding.service import (
    PromotionRuleFundingService,
)


router = APIRouter(
    tags=["Admin - Promotion Rule Funding"],
)


# ============================================================
# LISTAR FUENTES DE FINANCIACION DE UNA REGLA
# ============================================================

@router.get(
    "/promotion-rules/{rule_id}/funding",
    response_model=list[PromotionRuleFundingResponse],
    status_code=status.HTTP_200_OK,
)
async def list_rule_funding(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleFundingService(db)

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
# ASOCIAR FUENTE DE FINANCIACION A UNA REGLA
# ============================================================

@router.post(
    "/promotion-rules/{rule_id}/funding",
    response_model=PromotionRuleFundingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_funding_to_rule(
    rule_id: uuid.UUID,
    data: PromotionRuleFundingCreateForRule,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleFundingService(db)

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
# ACTUALIZAR APORTE DE UNA FUENTE
# ============================================================

@router.patch(
    "/promotion-rules/{rule_id}/funding/{funding_source_id}",
    response_model=PromotionRuleFundingResponse,
    status_code=status.HTTP_200_OK,
)
async def update_rule_funding(
    rule_id: uuid.UUID,
    funding_source_id: uuid.UUID,
    data: PromotionRuleFundingUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleFundingService(db)

    try:
        return await service.update(
            promotion_rule_id=rule_id,
            funding_source_id=funding_source_id,
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
# ELIMINAR FUENTE DE UNA REGLA
# ============================================================

@router.delete(
    "/promotion-rules/{rule_id}/funding/{funding_source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_funding_from_rule(
    rule_id: uuid.UUID,
    funding_source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleFundingService(db)

    try:
        await service.delete(
            promotion_rule_id=rule_id,
            funding_source_id=funding_source_id,
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
# LISTAR REGLAS ASOCIADAS A UNA FUENTE DE FINANCIACION
# ============================================================

@router.get(
    "/promotion-funding-sources/{funding_source_id}/promotion-rules",
    response_model=list[PromotionRuleFundingResponse],
    status_code=status.HTTP_200_OK,
)
async def list_funding_source_rules(
    funding_source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleFundingService(db)

    try:
        return await service.find_all_by_funding_source(
            funding_source_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
