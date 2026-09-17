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
from app.modules.model_spec_values.schemas import (
    ModelSpecValueCreateForModel,
    ModelSpecValueResponse,
    ModelSpecValueUpdate,
)
from app.modules.model_spec_values.service import (
    ModelSpecValueService,
)


router = APIRouter(
    tags=["Admin - Motorcycle Specifications"],
)


# ============================================================
# LISTAR ESPECIFICACIONES DE UNA MOTOCICLETA
# ============================================================

@router.get(
    "/motorcycles/{motorcycle_id}/specifications",
    response_model=list[ModelSpecValueResponse],
    status_code=status.HTTP_200_OK,
)
async def list_motorcycle_specifications(
    motorcycle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ModelSpecValueService(db)

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
# CREAR ESPECIFICACION PARA UNA MOTOCICLETA
# ============================================================

@router.post(
    "/motorcycles/{motorcycle_id}/specifications",
    response_model=ModelSpecValueResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_motorcycle_specification(
    motorcycle_id: uuid.UUID,
    data: ModelSpecValueCreateForModel,
    db: AsyncSession = Depends(get_db),
):
    service = ModelSpecValueService(db)

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
# OBTENER VALOR DE ESPECIFICACION POR ID
# ============================================================

@router.get(
    "/model-spec-values/{value_id}",
    response_model=ModelSpecValueResponse,
    status_code=status.HTTP_200_OK,
)
async def get_model_spec_value(
    value_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ModelSpecValueService(db)

    try:
        return await service.find_by_id(
            value_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR VALOR
# ============================================================

@router.patch(
    "/model-spec-values/{value_id}",
    response_model=ModelSpecValueResponse,
    status_code=status.HTTP_200_OK,
)
async def update_model_spec_value(
    value_id: uuid.UUID,
    data: ModelSpecValueUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ModelSpecValueService(db)

    try:
        return await service.update(
            value_id=value_id,
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
# ELIMINAR ESPECIFICACION DE UNA MOTOCICLETA
# ============================================================

@router.delete(
    "/model-spec-values/{value_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_model_spec_value(
    value_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ModelSpecValueService(db)

    try:
        await service.delete(
            value_id
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc