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
from app.modules.motorcycle_variants.schemas import (
    MotorcycleVariantCreateForModel,
    MotorcycleVariantResponse,
    MotorcycleVariantUpdate,
)
from app.modules.motorcycle_variants.service import (
    MotorcycleVariantService,
)


router = APIRouter(
    tags=["Admin - Motorcycle Variants"],
)


# ============================================================
# LISTAR VARIANTES DE UNA MOTOCICLETA
# ============================================================

@router.get(
    "/motorcycles/{motorcycle_id}/variants",
    response_model=list[MotorcycleVariantResponse],
    status_code=status.HTTP_200_OK,
)
async def list_motorcycle_variants(
    motorcycle_id: uuid.UUID,
    active: bool | None = Query(
        default=None,
        description="Filtrar variantes activas o inactivas",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleVariantService(db)

    try:
        return await service.find_all_by_model(
            model_id=motorcycle_id,
            active=active,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR VARIANTE PARA UNA MOTOCICLETA
# ============================================================

@router.post(
    "/motorcycles/{motorcycle_id}/variants",
    response_model=MotorcycleVariantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_motorcycle_variant(
    motorcycle_id: uuid.UUID,
    data: MotorcycleVariantCreateForModel,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleVariantService(db)

    try:
        return await service.create_for_model(
            model_id=motorcycle_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# OBTENER VARIANTE POR ID
# ============================================================

@router.get(
    "/motorcycle-variants/{variant_id}",
    response_model=MotorcycleVariantResponse,
    status_code=status.HTTP_200_OK,
)
async def get_motorcycle_variant(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleVariantService(db)

    try:
        return await service.find_by_id(
            variant_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR VARIANTE
# ============================================================

@router.patch(
    "/motorcycle-variants/{variant_id}",
    response_model=MotorcycleVariantResponse,
    status_code=status.HTTP_200_OK,
)
async def update_motorcycle_variant(
    variant_id: uuid.UUID,
    data: MotorcycleVariantUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleVariantService(db)

    try:
        return await service.update(
            variant_id=variant_id,
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
# DESACTIVAR VARIANTE
# ============================================================

@router.delete(
    "/motorcycle-variants/{variant_id}",
    response_model=MotorcycleVariantResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_motorcycle_variant(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleVariantService(db)

    try:
        return await service.deactivate(
            variant_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
