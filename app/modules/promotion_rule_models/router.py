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
from app.modules.promotion_rule_models.schemas import (
    PromotionRuleModelCreateForRule,
    PromotionRuleModelResponse,
)
from app.modules.promotion_rule_models.service import (
    PromotionRuleModelService,
)


router = APIRouter(
    tags=["Admin - Promotion Rule Models"],
)


# ============================================================
# LISTAR MODELOS ASOCIADOS A UNA REGLA
# ============================================================

@router.get(
    "/promotion-rules/{rule_id}/models",
    response_model=list[PromotionRuleModelResponse],
    status_code=status.HTTP_200_OK,
)
async def list_rule_models(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleModelService(db)

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
# ASOCIAR MODELO A UNA REGLA
# ============================================================

@router.post(
    "/promotion-rules/{rule_id}/models",
    response_model=PromotionRuleModelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_model_to_rule(
    rule_id: uuid.UUID,
    data: PromotionRuleModelCreateForRule,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleModelService(db)

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
# ELIMINAR MODELO DE UNA REGLA
# ============================================================

@router.delete(
    "/promotion-rules/{rule_id}/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_model_from_rule(
    rule_id: uuid.UUID,
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleModelService(db)

    try:
        await service.delete(
            promotion_rule_id=rule_id,
            model_id=model_id,
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
# LISTAR REGLAS ASOCIADAS A UNA MOTOCICLETA
# ============================================================

@router.get(
    "/motorcycles/{model_id}/promotion-rules",
    response_model=list[PromotionRuleModelResponse],
    status_code=status.HTTP_200_OK,
)
async def list_model_promotion_rules(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionRuleModelService(db)

    try:
        return await service.find_all_by_model(
            model_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc