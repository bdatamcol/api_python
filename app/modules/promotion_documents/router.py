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
from app.modules.promotion_documents.schemas import (
    PromotionDocumentCreateForCampaign,
    PromotionDocumentResponse,
    PromotionDocumentUpdate,
)
from app.modules.promotion_documents.service import (
    PromotionDocumentService,
)


router = APIRouter(
    tags=["Admin - Promotion Documents"],
)


# ============================================================
# LISTAR DOCUMENTOS DE UNA CAMPAÑA
# ============================================================

@router.get(
    "/promotion-campaigns/{campaign_id}/documents",
    response_model=list[PromotionDocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_campaign_documents(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionDocumentService(db)

    try:
        return await service.find_all_by_campaign(
            campaign_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR DOCUMENTO PARA UNA CAMPAÑA
# ============================================================

@router.post(
    "/promotion-campaigns/{campaign_id}/documents",
    response_model=PromotionDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign_document(
    campaign_id: uuid.UUID,
    data: PromotionDocumentCreateForCampaign,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionDocumentService(db)

    try:
        return await service.create_for_campaign(
            campaign_id=campaign_id,
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
    "/promotion-documents/{document_id}",
    response_model=PromotionDocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_promotion_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionDocumentService(db)

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
    "/promotion-documents/{document_id}",
    response_model=PromotionDocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_promotion_document(
    document_id: uuid.UUID,
    data: PromotionDocumentUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionDocumentService(db)

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
# ELIMINAR DOCUMENTO
# ============================================================

@router.delete(
    "/promotion-documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_promotion_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PromotionDocumentService(db)

    try:
        await service.delete(
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
