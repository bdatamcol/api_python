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
from app.modules.motorcycles.schemas import (
    MotorcycleCreate,
    MotorcycleResponse,
    MotorcycleUpdate,
)
from app.modules.motorcycles.service import MotorcycleService


router = APIRouter(
    prefix="/motorcycles",
    tags=["Admin - Motorcycles"],
)


# ============================================================
# LISTAR / FILTRAR MOTOCICLETAS
# ============================================================

@router.get(
    "",
    response_model=list[MotorcycleResponse],
    status_code=status.HTTP_200_OK,
)
async def list_motorcycles(
    active: bool | None = Query(
        default=None,
        description="Filtrar motocicletas activas o inactivas",
    ),
    brand_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar por marca",
    ),
    category_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar por categoría",
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        description="Buscar por nombre, slug o descripción corta",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleService(db)

    return await service.find_all(
        active=active,
        brand_id=brand_id,
        category_id=category_id,
        search=search,
    )


# ============================================================
# OBTENER MOTOCICLETA POR ID
# ============================================================

@router.get(
    "/{motorcycle_id}",
    response_model=MotorcycleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_motorcycle(
    motorcycle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleService(db)

    try:
        return await service.find_by_id(
            motorcycle_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR MOTOCICLETA
# ============================================================

@router.post(
    "",
    response_model=MotorcycleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_motorcycle(
    data: MotorcycleCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleService(db)

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
# ACTUALIZAR MOTOCICLETA
# ============================================================

@router.patch(
    "/{motorcycle_id}",
    response_model=MotorcycleResponse,
    status_code=status.HTTP_200_OK,
)
async def update_motorcycle(
    motorcycle_id: uuid.UUID,
    data: MotorcycleUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleService(db)

    try:
        return await service.update(
            motorcycle_id,
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
# DESACTIVAR MOTOCICLETA
# ============================================================

@router.delete(
    "/{motorcycle_id}",
    response_model=MotorcycleResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_motorcycle(
    motorcycle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleService(db)

    try:
        return await service.deactivate(
            motorcycle_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
