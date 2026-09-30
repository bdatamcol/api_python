import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.inventory.schemas import (
    InventoryCreateForVariant,
    InventoryResponse,
    InventoryUpdate,
)
from app.modules.inventory.service import (
    InventoryService,
)


router = APIRouter(
    tags=["Admin - Inventory"],
)


# ============================================================
# LISTAR INVENTARIO DE UNA VARIANTE
# ============================================================

@router.get(
    "/motorcycle-variants/{variant_id}/inventory",
    response_model=list[InventoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_variant_inventory(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return await service.find_all_by_variant(
            variant_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# LISTAR SOLO INVENTARIO DISPONIBLE
#
# available_quantity > 0
# ============================================================

@router.get(
    "/motorcycle-variants/{variant_id}/inventory/available",
    response_model=list[InventoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_available_variant_inventory(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return await service.find_available_by_variant(
            variant_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR INVENTARIO PARA UNA VARIANTE
# ============================================================

@router.post(
    "/motorcycle-variants/{variant_id}/inventory",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_variant_inventory(
    variant_id: uuid.UUID,
    data: InventoryCreateForVariant,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return await service.create_for_variant(
            variant_id=variant_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# LISTAR INVENTARIO DE UNA TIENDA
# ============================================================

@router.get(
    "/stores/{store_id}/inventory",
    response_model=list[InventoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_store_inventory(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return await service.find_all_by_store(
            store_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# OBTENER INVENTARIO POR ID
# ============================================================

@router.get(
    "/inventory/{inventory_id}",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_inventory(
    inventory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return await service.find_by_id(
            inventory_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR INVENTARIO
# ============================================================

@router.patch(
    "/inventory/{inventory_id}",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_inventory(
    inventory_id: uuid.UUID,
    data: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)

    try:
        return await service.update(
            inventory_id=inventory_id,
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
