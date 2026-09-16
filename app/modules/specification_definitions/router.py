import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.specification_definitions.schemas import (
    SpecificationDefinitionCreate,
    SpecificationDefinitionResponse,
    SpecificationDefinitionUpdate,
)
from app.modules.specification_definitions.service import (
    SpecificationDefinitionService,
)


router = APIRouter(
    prefix="/specification-definitions",
    tags=["Admin - Specification Definitions"],
)


# ============================================================
# LISTAR DEFINICIONES
# ============================================================

@router.get(
    "",
    response_model=list[SpecificationDefinitionResponse],
    status_code=status.HTTP_200_OK,
)
async def list_specification_definitions(
    db: AsyncSession = Depends(get_db),
):
    service = SpecificationDefinitionService(db)

    return await service.find_all()


# ============================================================
# OBTENER DEFINICION POR ID
# ============================================================

@router.get(
    "/{specification_id}",
    response_model=SpecificationDefinitionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_specification_definition(
    specification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = SpecificationDefinitionService(db)

    try:
        return await service.find_by_id(
            specification_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR DEFINICION
# ============================================================

@router.post(
    "",
    response_model=SpecificationDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_specification_definition(
    data: SpecificationDefinitionCreate,
    db: AsyncSession = Depends(get_db),
):
    service = SpecificationDefinitionService(db)

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
# ACTUALIZAR DEFINICION
# ============================================================

@router.patch(
    "/{specification_id}",
    response_model=SpecificationDefinitionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_specification_definition(
    specification_id: uuid.UUID,
    data: SpecificationDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = SpecificationDefinitionService(db)

    try:
        return await service.update(
            specification_id=specification_id,
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