import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.model_documents.model import (
    ModelDocument,
)


class ModelDocumentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR DOCUMENTOS DE UN MODELO
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[ModelDocument]:

        query = select(
            ModelDocument
        ).where(
            ModelDocument.model_id == model_id
        )

        if active is not None:
            query = query.where(
                ModelDocument.active == active
            )

        query = query.order_by(
            ModelDocument.created_at.desc()
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
    ) -> ModelDocument | None:

        query = select(
            ModelDocument
        ).where(
            ModelDocument.id == document_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR DOCUMENTO
    # ============================================================

    async def create(
        self,
        *,
        model_id: uuid.UUID,
        title: str,
        document_type: str | None = None,
        storage_key: str | None = None,
        source_url: str | None = None,
        metadata: object | None = None,
        active: bool = True,
    ) -> ModelDocument:

        document = ModelDocument(
            model_id=model_id,
            title=title,
            document_type=document_type,
            storage_key=storage_key,
            source_url=source_url,

            # En Python usamos metadata_json,
            # pero apunta a la columna PostgreSQL "metadata".
            metadata_json=metadata,

            active=active,
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
    # El service combinará los valores actuales con los campos
    # recibidos mediante PATCH antes de llamar este método.
    #
    # No modificamos:
    #
    # id
    # model_id
    # created_at
    # ============================================================

    async def update(
        self,
        document: ModelDocument,
        *,
        title: str,
        document_type: str | None,
        storage_key: str | None,
        source_url: str | None,
        metadata: object | None,
        active: bool,
    ) -> ModelDocument:

        document.title = title
        document.document_type = document_type
        document.storage_key = storage_key
        document.source_url = source_url
        document.metadata_json = metadata
        document.active = active

        await self.db.flush()
        await self.db.refresh(
            document
        )

        return document

    # ============================================================
    # DESACTIVAR DOCUMENTO
    #
    # model_documents sí tiene active, por lo que preferimos
    # conservar el registro en lugar de borrarlo físicamente.
    # ============================================================

    async def deactivate(
        self,
        document: ModelDocument,
    ) -> ModelDocument:

        document.active = False

        await self.db.flush()
        await self.db.refresh(
            document
        )

        return document
