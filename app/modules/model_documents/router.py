import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.model_documents.schemas import (
    ModelDocumentCreateForModel,
    ModelDocumentResponse,
    ModelDocumentUpdate,
)
from app.modules.model_documents.service import (
    ModelDocumentService,
)


router = APIRouter(
    tags=["Admin - Model Documents"],
)


# ============================================================
# LISTAR DOCUMENTOS DE UN MODELO
#
# active:
#
# true  -> solo activos
# false -> solo inactivos
# null  -> todos
# ============================================================

@router.get(
    "/motorcycles/{model_id}/documents",
    response_model=list[ModelDocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_model_documents(
    model_id: uuid.UUID,
    active: bool | None = Query(
        default=None
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ModelDocumentService(db)

    try:
        return await service.find_all_by_model(
            model_id=model_id,
            active=active,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR DOCUMENTO PARA UN MODELO
# ============================================================

@router.post(
    "/motorcycles/{model_id}/documents",
    response_model=ModelDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_model_document(
    model_id: uuid.UUID,
    data: ModelDocumentCreateForModel,
    db: AsyncSession = Depends(get_db),
):
    service = ModelDocumentService(db)

    try:
        return await service.create_for_model(
            model_id=model_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# OBTENER DOCUMENTO POR ID
# ============================================================

@router.get(
    "/model-documents/{document_id}",
    response_model=ModelDocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_model_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ModelDocumentService(db)

    try:
        return await service.find_by_id(
            document_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR DOCUMENTO
# ============================================================

@router.patch(
    "/model-documents/{document_id}",
    response_model=ModelDocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_model_document(
    document_id: uuid.UUID,
    data: ModelDocumentUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ModelDocumentService(db)

    try:
        return await service.update(
            document_id=document_id,
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
# DESACTIVAR DOCUMENTO
#
# No hacemos DELETE físico.
#
# Cambia:
#
# active = false
# ============================================================

@router.delete(
    "/model-documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_model_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ModelDocumentService(db)

    try:
        await service.deactivate(
            document_id
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
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
