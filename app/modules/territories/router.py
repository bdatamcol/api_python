import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.territories.schemas import (
    TerritoryCreate,
    TerritoryResponse,
    TerritoryType,
    TerritoryUpdate,
)
from app.modules.territories.service import TerritoryService


router = APIRouter(
    prefix="/territories",
    tags=["Admin - Territories"],
)


# ============================================================
# LISTAR TERRITORIOS
# ============================================================

@router.get(
    "",
    response_model=list[TerritoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_territories(
    active: bool | None = Query(
        default=None,
        description="Filtrar territorios activos o inactivos",
    ),
    territory_type: TerritoryType | None = Query(
        default=None,
        description="Filtrar por tipo de territorio",
    ),
    parent_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar por territorio padre",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TerritoryService(db)

    return await service.find_all(
        active=active,
        territory_type=territory_type,
        parent_id=parent_id,
    )


# ============================================================
# OBTENER TERRITORIO POR ID
# ============================================================

@router.get(
    "/{territory_id}",
    response_model=TerritoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_territory(
    territory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = TerritoryService(db)

    try:
        return await service.find_by_id(
            territory_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# OBTENER HIJOS DE UN TERRITORIO
# ============================================================

@router.get(
    "/{territory_id}/children",
    response_model=list[TerritoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_territory_children(
    territory_id: uuid.UUID,
    active: bool | None = Query(
        default=None,
        description="Filtrar hijos activos o inactivos",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TerritoryService(db)

    try:
        return await service.find_children(
            territory_id=territory_id,
            active=active,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR TERRITORIO
# ============================================================

@router.post(
    "",
    response_model=TerritoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_territory(
    data: TerritoryCreate,
    db: AsyncSession = Depends(get_db),
):
    service = TerritoryService(db)

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
# ACTUALIZAR TERRITORIO
# ============================================================

@router.patch(
    "/{territory_id}",
    response_model=TerritoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_territory(
    territory_id: uuid.UUID,
    data: TerritoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = TerritoryService(db)

    try:
        return await service.update(
            territory_id,
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
# DESACTIVAR TERRITORIO
# ============================================================

@router.delete(
    "/{territory_id}",
    response_model=TerritoryResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_territory(
    territory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = TerritoryService(db)

    try:
        return await service.deactivate(
            territory_id
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
