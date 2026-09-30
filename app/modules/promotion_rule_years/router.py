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
from app.modules.promotion_rule_years.schemas import (
    PromotionRuleYearCreateForRule,
    PromotionRuleYearResponse,
)
from app.modules.promotion_rule_years.service import (
    PromotionRuleYearService,
)


router = APIRouter(
    tags=["Admin - Promotion Rule Years"],
)


# ============================================================
# LISTAR AÑOS ASOCIADOS A UNA REGLA
# ============================================================

@router.get(
    "/promotion-rules/{rule_id}/years",
    response_model=list[PromotionRuleYearResponse],
    status_code=status.HTTP_200_OK,
)
async def list_rule_years(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleYearService(db)

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
# ASOCIAR AÑO A UNA REGLA
# ============================================================

@router.post(
    "/promotion-rules/{rule_id}/years",
    response_model=PromotionRuleYearResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_year_to_rule(
    rule_id: uuid.UUID,
    data: PromotionRuleYearCreateForRule,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleYearService(db)

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
# ELIMINAR AÑO DE UNA REGLA
# ============================================================

@router.delete(
    "/promotion-rules/{rule_id}/years/{model_year}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_year_from_rule(
    rule_id: uuid.UUID,
    model_year: int,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleYearService(db)

    try:
        await service.delete(
            promotion_rule_id=rule_id,
            model_year=model_year,
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
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