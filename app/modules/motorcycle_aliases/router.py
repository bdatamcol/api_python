import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.motorcycle_aliases.schemas import (
    MotorcycleAliasCreateForModel,
    MotorcycleAliasResponse,
    MotorcycleAliasUpdate,
)
from app.modules.motorcycle_aliases.service import (
    MotorcycleAliasService,
)


router = APIRouter(
    tags=["Admin - Motorcycle Aliases"],
)


# ============================================================
# LISTAR ALIAS DE UNA MOTOCICLETA
# ============================================================

@router.get(
    "/motorcycles/{motorcycle_id}/aliases",
    response_model=list[MotorcycleAliasResponse],
    status_code=status.HTTP_200_OK,
)
async def list_motorcycle_aliases(
    motorcycle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleAliasService(db)

    try:
        return await service.find_all_by_model(
            motorcycle_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR ALIAS PARA UNA MOTOCICLETA
# ============================================================

@router.post(
    "/motorcycles/{motorcycle_id}/aliases",
    response_model=MotorcycleAliasResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_motorcycle_alias(
    motorcycle_id: uuid.UUID,
    data: MotorcycleAliasCreateForModel,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleAliasService(db)

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
# ACTUALIZAR ALIAS
# ============================================================

@router.patch(
    "/motorcycle-aliases/{alias_id}",
    response_model=MotorcycleAliasResponse,
    status_code=status.HTTP_200_OK,
)
async def update_motorcycle_alias(
    alias_id: uuid.UUID,
    data: MotorcycleAliasUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleAliasService(db)

    try:
        return await service.update(
            alias_id=alias_id,
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
# ELIMINAR ALIAS
# ============================================================

@router.delete(
    "/motorcycle-aliases/{alias_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_motorcycle_alias(
    alias_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MotorcycleAliasService(db)

    try:
        await service.delete(
            alias_id
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
