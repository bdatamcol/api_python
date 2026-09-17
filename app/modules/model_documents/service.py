import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.model_documents.model import (
    ModelDocument,
)
from app.modules.model_documents.repository import (
    ModelDocumentRepository,
)
from app.modules.model_documents.schemas import (
    ModelDocumentCreateForModel,
    ModelDocumentUpdate,
)
from app.modules.motorcycles.repository import (
    MotorcycleRepository,
)


class ModelDocumentService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = ModelDocumentRepository(db)
        self.motorcycle_repository = MotorcycleRepository(db)

    # ============================================================
    # LISTAR DOCUMENTOS DE UN MODELO
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[ModelDocument]:

        await self._validate_model_exists(
            model_id
        )

        return await self.repository.find_all_by_model(
            model_id=model_id,
            active=active,
        )

    # ============================================================
    # BUSCAR DOCUMENTO POR ID
    # ============================================================

    async def find_by_id(
        self,
        document_id: uuid.UUID,
    ) -> ModelDocument:

        document = await self.repository.find_by_id(
            document_id
        )

        if document is None:
            raise LookupError(
                "El documento del modelo no existe"
            )

        return document

    # ============================================================
    # CREAR DOCUMENTO PARA UN MODELO
    # ============================================================

    async def create_for_model(
        self,
        model_id: uuid.UUID,
        data: ModelDocumentCreateForModel,
    ) -> ModelDocument:

        # ========================================================
        # VALIDAR MODELO ACTIVO
        # ========================================================

        await self._validate_active_model(
            model_id
        )

        # ========================================================
        # VALIDAR TITULO
        # ========================================================

        title = data.title.strip()

        if not title:
            raise ValueError(
                "El título del documento no puede estar vacío"
            )

        try:
            document = await self.repository.create(
                model_id=model_id,
                title=title,
                document_type=data.document_type,
                storage_key=data.storage_key,
                source_url=data.source_url,
                metadata=data.metadata,
                active=data.active,
            )

            await self.db.commit()

            await self.db.refresh(
                document
            )

            return document

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear el documento del modelo"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR DOCUMENTO
    # ============================================================

    async def update(
        self,
        document_id: uuid.UUID,
        data: ModelDocumentUpdate,
    ) -> ModelDocument:

        document = await self.repository.find_by_id(
            document_id
        )

        if document is None:
            raise LookupError(
                "El documento del modelo no existe"
            )

        fields_set = data.model_fields_set

        # ========================================================
        # PATCH VACIO
        # ========================================================

        if not fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar"
            )

        # ========================================================
        # TITLE ES NOT NULL
        # ========================================================

        if (
            "title" in fields_set
            and data.title is None
        ):
            raise ValueError(
                "title no puede ser null"
            )

        # ========================================================
        # ACTIVE ES NOT NULL
        # ========================================================

        if (
            "active" in fields_set
            and data.active is None
        ):
            raise ValueError(
                "active no puede ser null"
            )

        # ========================================================
        # CONSERVAR CAMPOS NO ENVIADOS
        # ========================================================

        title = (
            data.title
            if "title" in fields_set
            else document.title
        )

        document_type = (
            data.document_type
            if "document_type" in fields_set
            else document.document_type
        )

        storage_key = (
            data.storage_key
            if "storage_key" in fields_set
            else document.storage_key
        )

        source_url = (
            data.source_url
            if "source_url" in fields_set
            else document.source_url
        )

        metadata = (
            data.metadata
            if "metadata" in fields_set
            else document.metadata_json
        )

        active = (
            data.active
            if "active" in fields_set
            else document.active
        )

        # ========================================================
        # VALIDAR TITULO FINAL
        # ========================================================

        title = title.strip()

        if not title:
            raise ValueError(
                "El título del documento no puede estar vacío"
            )

        try:
            updated = await self.repository.update(
                document,
                title=title,
                document_type=document_type,
                storage_key=storage_key,
                source_url=source_url,
                metadata=metadata,
                active=active,
            )

            await self.db.commit()

            await self.db.refresh(
                updated
            )

            return updated

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar el documento del modelo"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR DOCUMENTO
    #
    # No hacemos DELETE físico porque model_documents
    # tiene columna active.
    # ============================================================

    async def deactivate(
        self,
        document_id: uuid.UUID,
    ) -> ModelDocument:

        document = await self.repository.find_by_id(
            document_id
        )

        if document is None:
            raise LookupError(
                "El documento del modelo no existe"
            )

        if not document.active:
            raise ValueError(
                "El documento ya se encuentra inactivo"
            )

        try:
            document = await self.repository.deactivate(
                document
            )

            await self.db.commit()

            await self.db.refresh(
                document
            )

            return document

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR MODELO
    # ============================================================

    async def _validate_model_exists(
        self,
        model_id: uuid.UUID,
    ):
        motorcycle = await self.motorcycle_repository.find_by_id(
            model_id
        )

        if motorcycle is None:
            raise ValueError(
                "El modelo de motocicleta seleccionado no existe"
            )

        return motorcycle

    # ============================================================
    # VALIDAR MODELO ACTIVO
    # ============================================================

    async def _validate_active_model(
        self,
        model_id: uuid.UUID,
    ):
        motorcycle = await self._validate_model_exists(
            model_id
        )

        if not motorcycle.active:
            raise ValueError(
                "El modelo de motocicleta seleccionado está inactivo"
            )

        return motorcycle
