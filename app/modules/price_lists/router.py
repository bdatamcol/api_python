import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.price_lists.schemas import (
    PriceListCreate,
    PriceListResponse,
    PriceListUpdate,
)
from app.modules.price_lists.service import PriceListService


router = APIRouter(
    prefix="/price-lists",
    tags=["Admin - Price Lists"],
)


# ============================================================
# LISTAR LISTAS DE PRECIOS
# ============================================================

@router.get(
    "",
    response_model=list[PriceListResponse],
    status_code=status.HTTP_200_OK,
)
async def list_price_lists(
    active: bool | None = Query(
        default=None,
        description="Filtrar listas activas o inactivas",
    ),
    territory_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar por territorio",
    ),
    store_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar por sede",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PriceListService(db)

    return await service.find_all(
        active=active,
        territory_id=territory_id,
        store_id=store_id,
    )


# ============================================================
# OBTENER LISTA POR ID
# ============================================================

@router.get(
    "/{price_list_id}",
    response_model=PriceListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_price_list(
    price_list_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PriceListService(db)

    try:
        return await service.find_by_id(
            price_list_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR LISTA DE PRECIOS
# ============================================================

@router.post(
    "",
    response_model=PriceListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_price_list(
    data: PriceListCreate,
    db: AsyncSession = Depends(get_db),
):
    service = PriceListService(db)

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
# ACTUALIZAR LISTA DE PRECIOS
# ============================================================

@router.patch(
    "/{price_list_id}",
    response_model=PriceListResponse,
    status_code=status.HTTP_200_OK,
)
async def update_price_list(
    price_list_id: uuid.UUID,
    data: PriceListUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PriceListService(db)

    try:
        return await service.update(
            price_list_id,
            data,
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
# DESACTIVAR LISTA DE PRECIOS
# ============================================================

@router.delete(
    "/{price_list_id}",
    response_model=PriceListResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_price_list(
    price_list_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PriceListService(db)

    try:
        return await service.deactivate(
            price_list_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
