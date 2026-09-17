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
from app.modules.promotion_rule_variants.schemas import (
    PromotionRuleVariantCreateForRule,
    PromotionRuleVariantResponse,
)
from app.modules.promotion_rule_variants.service import (
    PromotionRuleVariantService,
)


router = APIRouter(
    tags=["Admin - Promotion Rule Variants"],
)


# ============================================================
# LISTAR VARIANTES ASOCIADAS A UNA REGLA
# ============================================================

@router.get(
    "/promotion-rules/{rule_id}/variants",
    response_model=list[PromotionRuleVariantResponse],
    status_code=status.HTTP_200_OK,
)
async def list_rule_variants(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleVariantService(db)

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
# ASOCIAR VARIANTE A UNA REGLA
# ============================================================

@router.post(
    "/promotion-rules/{rule_id}/variants",
    response_model=PromotionRuleVariantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_variant_to_rule(
    rule_id: uuid.UUID,
    data: PromotionRuleVariantCreateForRule,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleVariantService(db)

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
# QUITAR VARIANTE DE UNA REGLA
# ============================================================

@router.delete(
    "/promotion-rules/{rule_id}/variants/{variant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_variant_from_rule(
    rule_id: uuid.UUID,
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleVariantService(db)

    try:
        await service.delete(
            promotion_rule_id=rule_id,
            variant_id=variant_id,
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
# LISTAR REGLAS ASOCIADAS A UNA VARIANTE
# ============================================================

@router.get(
    "/motorcycle-variants/{variant_id}/promotion-rules",
    response_model=list[PromotionRuleVariantResponse],
    status_code=status.HTTP_200_OK,
)
async def list_variant_promotion_rules(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleVariantService(db)

    try:
        return await service.find_all_by_variant(
            variant_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc