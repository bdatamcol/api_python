import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_campaigns.repository import (
    PromotionCampaignRepository,
)
from app.modules.promotion_documents.model import (
    PromotionDocument,
)
from app.modules.promotion_documents.repository import (
    PromotionDocumentRepository,
)
from app.modules.promotion_documents.schemas import (
    PromotionDocumentCreateForCampaign,
    PromotionDocumentUpdate,
)


class PromotionDocumentService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PromotionDocumentRepository(db)

        self.campaign_repository = PromotionCampaignRepository(db)

    # ============================================================
    # LISTAR DOCUMENTOS DE UNA CAMPAÑA
    # ============================================================

    async def find_all_by_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> list[PromotionDocument]:

        await self._validate_campaign_exists(
            campaign_id
        )

        return await self.repository.find_all_by_campaign(
            campaign_id
        )

    # ============================================================
    # BUSCAR DOCUMENTO POR ID
    # ============================================================

    async def find_by_id(
        self,
        document_id: uuid.UUID,
    ) -> PromotionDocument:

        document = await self.repository.find_by_id(
            document_id
        )

        if document is None:
            raise LookupError(
                "El documento promocional no existe"
            )

        return document

    # ============================================================
    # CREAR DOCUMENTO PARA UNA CAMPAÑA
    # ============================================================

    async def create_for_campaign(
        self,
        campaign_id: uuid.UUID,
        data: PromotionDocumentCreateForCampaign,
    ) -> PromotionDocument:

        # ========================================================
        # VALIDAR QUE LA CAMPAÑA EXISTA
        #
        # No bloqueamos por status.
        #
        # Una campaña DRAFT, ACTIVE, EXPIRED o CANCELLED puede
        # conservar documentos históricos asociados.
        # ========================================================

        await self._validate_campaign_exists(
            campaign_id
        )

        try:
            document = await self.repository.create(
                campaign_id=campaign_id,
                document_type=data.document_type,
                original_name=data.original_name,
                storage_key=data.storage_key,
                source_url=data.source_url,
                received_at=data.received_at,
                notes=data.notes,
                metadata=data.metadata,
            )

            await self.db.commit()

            await self.db.refresh(
                document
            )

            return document

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear el documento promocional"
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
        data: PromotionDocumentUpdate,
    ) -> PromotionDocument:

        document = await self.repository.find_by_id(
            document_id
        )

        if document is None:
            raise LookupError(
                "El documento promocional no existe"
            )

        # ========================================================
        # VALIDAR QUE EL PATCH TENGA AL MENOS UN CAMPO
        # ========================================================

        fields_set = data.model_fields_set

        if not fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar"
            )

        # ========================================================
        # document_type ES NOT NULL EN POSTGRESQL
        #
        # Por eso:
        #
        # {}
        #
        # es diferente de:
        #
        # {"document_type": null}
        # ========================================================

        if (
            "document_type" in fields_set
            and data.document_type is None
        ):
            raise ValueError(
                "document_type no puede ser null"
            )

        # ========================================================
        # CONSERVAR LOS VALORES NO ENVIADOS
        # ========================================================

        document_type = (
            data.document_type
            if "document_type" in fields_set
            else document.document_type
        )

        original_name = (
            data.original_name
            if "original_name" in fields_set
            else document.original_name
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

        received_at = (
            data.received_at
            if "received_at" in fields_set
            else document.received_at
        )

        notes = (
            data.notes
            if "notes" in fields_set
            else document.notes
        )

        metadata = (
            data.metadata
            if "metadata" in fields_set
            else document.metadata_json
        )

        try:
            updated = await self.repository.update(
                document,
                document_type=document_type,
                original_name=original_name,
                storage_key=storage_key,
                source_url=source_url,
                received_at=received_at,
                notes=notes,
                metadata=metadata,
            )

            await self.db.commit()

            await self.db.refresh(
                updated
            )

            return updated

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar el documento promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ELIMINAR DOCUMENTO
    #
    # Como promotion_documents no tiene active,
    # eliminamos físicamente el registro.
    #
    # Todavía NO eliminamos archivos de MinIO/S3.
    # ============================================================

    async def delete(
        self,
        document_id: uuid.UUID,
    ) -> None:

        document = await self.repository.find_by_id(
            document_id
        )

        if document is None:
            raise LookupError(
                "El documento promocional no existe"
            )

        try:
            await self.repository.delete(
                document
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR CAMPAÑA
    # ============================================================

    async def _validate_campaign_exists(
        self,
        campaign_id: uuid.UUID,
    ):
        campaign = await self.campaign_repository.find_by_id(
            campaign_id
        )

        if campaign is None:
            raise ValueError(
                "La campaña promocional seleccionada no existe"
            )

        return campaign
