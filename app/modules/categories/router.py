import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.modules.categories.service import CategoryService


router = APIRouter(
    prefix="/categories",
    tags=["Admin - Categories"],
)


# ============================================================
# LISTAR CATEGORIAS
# ============================================================

@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_categories(
    active: bool | None = Query(
        default=None,
        description="Filtrar por categorías activas o inactivas",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)

    return await service.find_all(
        active=active
    )


# ============================================================
# OBTENER CATEGORIA POR ID
# ============================================================

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)

    try:
        return await service.find_by_id(
            category_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR CATEGORIA
# ============================================================

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)

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
# ACTUALIZAR CATEGORIA
# ============================================================

@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)

    try:
        return await service.update(
            category_id,
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
# DESACTIVAR CATEGORIA
# ============================================================

@router.delete(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)

    try:
        return await service.deactivate(
            category_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
