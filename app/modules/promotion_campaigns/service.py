import re
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotion_campaigns.model import (
    PromotionCampaign,
)
from app.modules.promotion_campaigns.repository import (
    PromotionCampaignRepository,
)
from app.modules.promotion_campaigns.schemas import (
    PromotionCampaignCreate,
    PromotionCampaignStatus,
    PromotionCampaignUpdate,
)


class PromotionCampaignService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PromotionCampaignRepository(db)

    # ============================================================
    # LISTAR CAMPAÑAS
    # ============================================================

    async def find_all(
        self,
        status: PromotionCampaignStatus | None = None,
    ) -> list[PromotionCampaign]:

        status_value = (
            status.value
            if status is not None
            else None
        )

        return await self.repository.find_all(
            status=status_value
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        campaign_id: uuid.UUID,
    ) -> PromotionCampaign:

        campaign = await self.repository.find_by_id(
            campaign_id
        )

        if campaign is None:
            raise LookupError(
                "La campaña promocional no existe"
            )

        return campaign

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: PromotionCampaignCreate,
    ) -> PromotionCampaign:

        name = self._clean_required_text(
            data.name
        )

        description = self._clean_optional_text(
            data.description
        )

        self._validate_dates(
            start_date=data.start_date,
            end_date=data.end_date,
        )

        try:
            campaign = await self.repository.create(
                name=name,
                description=description,
                start_date=data.start_date,
                end_date=data.end_date,
                status=data.status.value,
                stackable=data.stackable,
            )

            await self.db.commit()
            await self.db.refresh(
                campaign
            )

            return campaign

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear la campaña promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        campaign_id: uuid.UUID,
        data: PromotionCampaignUpdate,
    ) -> PromotionCampaign:

        campaign = await self.repository.find_by_id(
            campaign_id
        )

        if campaign is None:
            raise LookupError(
                "La campaña promocional no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return campaign

        # ========================================================
        # NOMBRE
        # ========================================================

        if "name" in update_data:

            if update_data["name"] is None:
                raise ValueError(
                    "El nombre no puede ser nulo"
                )

            update_data["name"] = (
                self._clean_required_text(
                    update_data["name"]
                )
            )

        # ========================================================
        # DESCRIPCION
        #
        # Sí puede ser NULL.
        # ========================================================

        if "description" in update_data:
            update_data["description"] = (
                self._clean_optional_text(
                    update_data["description"]
                )
            )

        # ========================================================
        # CAMPOS OBLIGATORIOS NO PUEDEN QUEDAR NULL
        # ========================================================

        if (
            "start_date" in update_data
            and update_data["start_date"] is None
        ):
            raise ValueError(
                "La fecha inicial no puede ser nula"
            )

        if (
            "end_date" in update_data
            and update_data["end_date"] is None
        ):
            raise ValueError(
                "La fecha final no puede ser nula"
            )

        if (
            "status" in update_data
            and update_data["status"] is None
        ):
            raise ValueError(
                "El estado no puede ser nulo"
            )

        if (
            "stackable" in update_data
            and update_data["stackable"] is None
        ):
            raise ValueError(
                "El campo stackable no puede ser nulo"
            )

        # ========================================================
        # VALIDAR FECHAS FINALES
        #
        # Un PATCH podría enviar solamente start_date
        # o solamente end_date.
        # ========================================================

        final_start_date = update_data.get(
            "start_date",
            campaign.start_date,
        )

        final_end_date = update_data.get(
            "end_date",
            campaign.end_date,
        )

        self._validate_dates(
            start_date=final_start_date,
            end_date=final_end_date,
        )

        # ========================================================
        # CONVERTIR ENUM
        # ========================================================

        if "status" in update_data:
            if isinstance(
                update_data["status"],
                PromotionCampaignStatus,
            ):
                update_data["status"] = (
                    update_data["status"].value
                )

        try:
            campaign = await self.repository.update(
                campaign=campaign,
                data=update_data,
            )

            await self.db.commit()
            await self.db.refresh(
                campaign
            )

            return campaign

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar la campaña promocional"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # CANCELAR CAMPAÑA
    #
    # No hacemos DELETE físico.
    #
    # status = CANCELLED
    # ============================================================

    async def cancel(
        self,
        campaign_id: uuid.UUID,
    ) -> PromotionCampaign:

        campaign = await self.repository.find_by_id(
            campaign_id
        )

        if campaign is None:
            raise LookupError(
                "La campaña promocional no existe"
            )

        if (
            campaign.status
            == PromotionCampaignStatus.CANCELLED.value
        ):
            return campaign

        try:
            campaign = await self.repository.update(
                campaign=campaign,
                data={
                    "status": (
                        PromotionCampaignStatus
                        .CANCELLED
                        .value
                    )
                },
            )

            await self.db.commit()
            await self.db.refresh(
                campaign
            )

            return campaign

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR FECHAS
    # ============================================================

    @staticmethod
    def _validate_dates(
        start_date,
        end_date,
    ) -> None:

        if end_date < start_date:
            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial"
            )

    # ============================================================
    # LIMPIAR TEXTO OBLIGATORIO
    # ============================================================

    @staticmethod
    def _clean_required_text(
        value: str,
    ) -> str:

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        if not value:
            raise ValueError(
                "El nombre no puede estar vacío"
            )

        return value

    # ============================================================
    # LIMPIAR TEXTO OPCIONAL
    # ============================================================

    @staticmethod
    def _clean_optional_text(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value or None