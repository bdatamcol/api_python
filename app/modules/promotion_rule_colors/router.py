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
from app.modules.promotion_rule_colors.schemas import (
    PromotionRuleColorCreateForRule,
    PromotionRuleColorResponse,
)
from app.modules.promotion_rule_colors.service import (
    PromotionRuleColorService,
)


router = APIRouter(
    tags=["Admin - Promotion Rule Colors"],
)


# ============================================================
# LISTAR COLORES ASOCIADOS A UNA REGLA
# ============================================================

@router.get(
    "/promotion-rules/{rule_id}/colors",
    response_model=list[PromotionRuleColorResponse],
    status_code=status.HTTP_200_OK,
)
async def list_rule_colors(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleColorService(db)

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
# ASOCIAR COLOR A UNA REGLA
# ============================================================

@router.post(
    "/promotion-rules/{rule_id}/colors",
    response_model=PromotionRuleColorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_color_to_rule(
    rule_id: uuid.UUID,
    data: PromotionRuleColorCreateForRule,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleColorService(db)

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
# ELIMINAR COLOR DE UNA REGLA
# ============================================================

@router.delete(
    "/promotion-rules/{rule_id}/colors/{color_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_color_from_rule(
    rule_id: uuid.UUID,
    color_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleColorService(db)

    try:
        await service.delete(
            promotion_rule_id=rule_id,
            color_id=color_id,
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
# LISTAR REGLAS ASOCIADAS A UN COLOR
# ============================================================

@router.get(
    "/colors/{color_id}/promotion-rules",
    response_model=list[PromotionRuleColorResponse],
    status_code=status.HTTP_200_OK,
)
async def list_color_promotion_rules(
    color_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleColorService(db)

    try:
        return await service.find_all_by_color(
            color_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc