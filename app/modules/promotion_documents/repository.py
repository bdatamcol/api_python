import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_documents.model import (
    PromotionDocument,
)


class PromotionDocumentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR TODOS LOS DOCUMENTOS DE UNA CAMPAÑA
    # ============================================================

    async def find_all_by_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> list[PromotionDocument]:

        query = (
            select(PromotionDocument)
            .where(
                PromotionDocument.campaign_id
                == campaign_id
            )
            .order_by(
                PromotionDocument.created_at.desc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR DOCUMENTO POR ID
    # ============================================================

    async def find_by_id(
        self,
        document_id: uuid.UUID,
    ) -> PromotionDocument | None:

        query = select(
            PromotionDocument
        ).where(
            PromotionDocument.id
            == document_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR DOCUMENTO
    # ============================================================

    async def create(
        self,
        *,
        campaign_id: uuid.UUID,
        document_type: str,
        original_name: str | None = None,
        storage_key: str | None = None,
        source_url: str | None = None,
        received_at: datetime | None = None,
        notes: str | None = None,
        metadata: object | None = None,
    ) -> PromotionDocument:

        document = PromotionDocument(
            campaign_id=campaign_id,
            document_type=document_type,
            original_name=original_name,
            storage_key=storage_key,
            source_url=source_url,
            received_at=received_at,
            notes=notes,

            # ====================================================
            # IMPORTANTE
            #
            # En nuestro modelo SQLAlchemy:
            #
            # metadata_json
            #
            # apunta a la columna PostgreSQL:
            #
            # metadata
            # ====================================================

            metadata_json=metadata,
        )

        self.db.add(
            document
        )

        await self.db.flush()
        await self.db.refresh(
            document
        )

        return document

    # ============================================================
    # ACTUALIZAR DOCUMENTO
    #
    # El service será responsable de combinar:
    #
    # - valores existentes
    # - valores enviados mediante PATCH
    #
    # antes de llamar este método.
    # ============================================================

    async def update(
        self,
        document: PromotionDocument,
        *,
        document_type: str,
        original_name: str | None,
        storage_key: str | None,
        source_url: str | None,
        received_at: datetime | None,
        notes: str | None,
        metadata: object | None,
    ) -> PromotionDocument:

        document.document_type = document_type
        document.original_name = original_name
        document.storage_key = storage_key
        document.source_url = source_url
        document.received_at = received_at
        document.notes = notes

        document.metadata_json = metadata

        await self.db.flush()
        await self.db.refresh(
            document
        )

        return document

    # ============================================================
    # ELIMINAR DOCUMENTO
    #
    # Esta tabla no tiene "active", por lo que la eliminación
    # será física.
    #
    # IMPORTANTE:
    # esto elimina solamente el registro PostgreSQL.
    # Más adelante, cuando integremos MinIO/S3, tendremos que
    # decidir también qué hacer con el archivo físico.
    # ============================================================

    async def delete(
        self,
        document: PromotionDocument,
    ) -> None:

        await self.db.delete(
            document
        )

        await self.db.flush()
