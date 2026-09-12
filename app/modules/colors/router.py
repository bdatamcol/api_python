import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.colors.schemas import (
    ColorCreate,
    ColorResponse,
    ColorUpdate,
)
from app.modules.colors.service import ColorService


router = APIRouter(
    prefix="/colors",
    tags=["Admin - Colors"],
)


@router.get(
    "",
    response_model=list[ColorResponse],
    status_code=status.HTTP_200_OK,
)
async def list_colors(
    active: bool | None = Query(
        default=None,
        description="Filtrar por colores activos o inactivos",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ColorService(db)

    return await service.find_all(
        active=active
    )


@router.get(
    "/{color_id}",
    response_model=ColorResponse,
    status_code=status.HTTP_200_OK,
)
async def get_color(
    color_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ColorService(db)

    try:
        return await service.find_by_id(
            color_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ColorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_color(
    data: ColorCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ColorService(db)

    try:
        return await service.create(
            data
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{color_id}",
    response_model=ColorResponse,
    status_code=status.HTTP_200_OK,
)
async def update_color(
    color_id: uuid.UUID,
    data: ColorUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ColorService(db)

    try:
        return await service.update(
            color_id,
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


@router.delete(
    "/{color_id}",
    response_model=ColorResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_color(
    color_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ColorService(db)

    try:
        return await service.deactivate(
            color_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
