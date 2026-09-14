import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.stores.schemas import (
    StoreCreate,
    StoreResponse,
    StoreUpdate,
)
from app.modules.stores.service import StoreService


router = APIRouter(
    prefix="/stores",
    tags=["Admin - Stores"],
)


@router.get(
    "",
    response_model=list[StoreResponse],
    status_code=status.HTTP_200_OK,
)
async def list_stores(
    active: bool | None = Query(
        default=None,
        description="Filtrar sedes activas o inactivas",
    ),
    territory_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar sedes por territorio",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = StoreService(db)

    return await service.find_all(
        active=active,
        territory_id=territory_id,
    )


@router.get(
    "/{store_id}",
    response_model=StoreResponse,
    status_code=status.HTTP_200_OK,
)
async def get_store(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = StoreService(db)

    try:
        return await service.find_by_id(
            store_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=StoreResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_store(
    data: StoreCreate,
    db: AsyncSession = Depends(get_db),
):
    service = StoreService(db)

    try:
        return await service.create(
            data
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{store_id}",
    response_model=StoreResponse,
    status_code=status.HTTP_200_OK,
)
async def update_store(
    store_id: uuid.UUID,
    data: StoreUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = StoreService(db)

    try:
        return await service.update(
            store_id,
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


@router.delete(
    "/{store_id}",
    response_model=StoreResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_store(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = StoreService(db)

    try:
        return await service.deactivate(
            store_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
