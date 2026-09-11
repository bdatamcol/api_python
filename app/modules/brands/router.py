import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.brands.schemas import (
    BrandCreate,
    BrandResponse,
    BrandUpdate,
)
from app.modules.brands.service import BrandService


router = APIRouter(
    prefix="/brands",
    tags=["Admin - Brands"],
)


# ============================================================
# LISTAR MARCAS
# ============================================================

@router.get(
    "",
    response_model=list[BrandResponse],
    status_code=status.HTTP_200_OK,
)
async def list_brands(
    active: bool | None = Query(
        default=None,
        description="Filtrar por marcas activas o inactivas",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)

    return await service.find_all(
        active=active
    )


# ============================================================
# OBTENER MARCA POR ID
# ============================================================

@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
    status_code=status.HTTP_200_OK,
)
async def get_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)

    try:
        return await service.find_by_id(
            brand_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR MARCA
# ============================================================

@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_brand(
    data: BrandCreate,
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)

    try:
        return await service.create(
            data
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR MARCA
# ============================================================

@router.patch(
    "/{brand_id}",
    response_model=BrandResponse,
    status_code=status.HTTP_200_OK,
)
async def update_brand(
    brand_id: uuid.UUID,
    data: BrandUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)

    try:
        return await service.update(
            brand_id,
            data,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# ============================================================
# DESACTIVAR MARCA
# ============================================================

@router.delete(
    "/{brand_id}",
    response_model=BrandResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)

    try:
        return await service.deactivate(
            brand_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
