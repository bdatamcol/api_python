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
from app.modules.promotion_funding_sources.schemas import (
    PromotionFundingSourceCreate,
    PromotionFundingSourceResponse,
    PromotionFundingSourceUpdate,
)
from app.modules.promotion_funding_sources.service import (
    PromotionFundingSourceService,
)


router = APIRouter(
    prefix="/promotion-funding-sources",
    tags=["Admin - Promotion Funding Sources"],
)


# ============================================================
# LISTAR FUENTES DE FINANCIACION
# ============================================================

@router.get(
    "",
    response_model=list[PromotionFundingSourceResponse],
    status_code=status.HTTP_200_OK,
)
async def list_promotion_funding_sources(
    active: bool | None = Query(
        default=None,
        description="Filtrar fuentes activas o inactivas",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PromotionFundingSourceService(db)

    return await service.find_all(
        active=active
    )


# ============================================================
# OBTENER POR ID
# ============================================================

@router.get(
    "/{funding_source_id}",
    response_model=PromotionFundingSourceResponse,
    status_code=status.HTTP_200_OK,
)
async def get_promotion_funding_source(
    funding_source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionFundingSourceService(db)

    try:
        return await service.find_by_id(
            funding_source_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR
# ============================================================

@router.post(
    "",
    response_model=PromotionFundingSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_promotion_funding_source(
    data: PromotionFundingSourceCreate,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionFundingSourceService(db)

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
# ACTUALIZAR
# ============================================================

@router.patch(
    "/{funding_source_id}",
    response_model=PromotionFundingSourceResponse,
    status_code=status.HTTP_200_OK,
)
async def update_promotion_funding_source(
    funding_source_id: uuid.UUID,
    data: PromotionFundingSourceUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionFundingSourceService(db)

    try:
        return await service.update(
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
# DESACTIVAR
#
# No elimina físicamente:
#
# active = false
# ============================================================

@router.delete(
    "/{funding_source_id}",
    response_model=PromotionFundingSourceResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_promotion_funding_source(
    funding_source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionFundingSourceService(db)

    try:
        return await service.deactivate(
            funding_source_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc