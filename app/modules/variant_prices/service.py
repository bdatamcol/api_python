import uuid
from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motorcycle_variants.repository import (
    MotorcycleVariantRepository,
)
from app.modules.price_lists.repository import (
    PriceListRepository,
)
from app.modules.variant_prices.model import VariantPrice
from app.modules.variant_prices.repository import (
    VariantPriceRepository,
)
from app.modules.variant_prices.schemas import (
    VariantPriceCreateForVariant,
    VariantPriceUpdate,
)


class VariantPriceService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = VariantPriceRepository(db)
        self.variant_repository = MotorcycleVariantRepository(db)
        self.price_list_repository = PriceListRepository(db)

    # ============================================================
    # LISTAR HISTORIAL DE PRECIOS DE UNA VARIANTE
    # ============================================================

    async def find_all_by_variant(
        self,
        variant_id: uuid.UUID,
        price_list_id: uuid.UUID | None = None,
        active: bool | None = None,
    ) -> list[VariantPrice]:

        await self._validate_variant_exists(
            variant_id
        )

        if price_list_id is not None:
            await self._validate_price_list_exists(
                price_list_id
            )

        return await self.repository.find_all_by_variant(
            variant_id=variant_id,
            price_list_id=price_list_id,
            active=active,
        )

    # ============================================================
    # BUSCAR PRECIO POR ID
    # ============================================================

    async def find_by_id(
        self,
        price_id: uuid.UUID,
    ) -> VariantPrice:

        price = await self.repository.find_by_id(
            price_id
        )

        if price is None:
            raise LookupError(
                "El precio no existe"
            )

        return price

    # ============================================================
    # OBTENER PRECIO VIGENTE
    # ============================================================

    async def find_current(
        self,
        variant_id: uuid.UUID,
        price_list_id: uuid.UUID,
        on_date: date | None = None,
    ) -> VariantPrice:

        await self._validate_variant_exists(
            variant_id
        )

        await self._validate_price_list_exists(
            price_list_id
        )

        current_date = on_date or date.today()

        price = await self.repository.find_current(
            variant_id=variant_id,
            price_list_id=price_list_id,
            on_date=current_date,
        )

        if price is None:
            raise LookupError(
                "No existe un precio vigente para la variante y lista de precios seleccionadas"
            )

        return price

    # ============================================================
    # CREAR PRECIO PARA UNA VARIANTE
    # ============================================================

    async def create_for_variant(
        self,
        variant_id: uuid.UUID,
        data: VariantPriceCreateForVariant,
    ) -> VariantPrice:

        # La variante debe existir y estar activa
        await self._validate_active_variant(
            variant_id
        )

        # La lista debe existir y estar activa
        await self._validate_active_price_list(
            data.price_list_id
        )

        # Validación adicional de fechas.
        self._validate_dates(
            valid_from=data.valid_from,
            valid_until=data.valid_until,
        )

        # Normalizar referencia de origen.
        source_reference = self._clean_optional_text(
            data.source_reference
        )

        # ========================================================
        # BUSCAR CRUCES DE VIGENCIA
        # ========================================================

        overlapping = await self.repository.find_overlapping(
            variant_id=variant_id,
            price_list_id=data.price_list_id,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
        )

        if overlapping:
            raise ValueError(
                "Ya existe un precio activo cuya vigencia se cruza con el periodo indicado"
            )

        try:
            price = await self.repository.create(
                variant_id=variant_id,
                price_list_id=data.price_list_id,
                amount=data.amount,
                valid_from=data.valid_from,
                valid_until=data.valid_until,
                source_reference=source_reference,
            )

            await self.db.commit()
            await self.db.refresh(price)

            return price

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear el precio porque su vigencia entra en conflicto con otro precio existente"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR PRECIO
    # ============================================================

    async def update(
        self,
        price_id: uuid.UUID,
        data: VariantPriceUpdate,
    ) -> VariantPrice:

        price = await self.repository.find_by_id(
            price_id
        )

        if price is None:
            raise LookupError(
                "El precio no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return price

        # ========================================================
        # CAMPOS QUE NO PUEDEN SER NULL
        # ========================================================

        if (
            "amount" in update_data
            and update_data["amount"] is None
        ):
            raise ValueError(
                "El monto del precio no puede ser nulo"
            )

        if (
            "valid_from" in update_data
            and update_data["valid_from"] is None
        ):
            raise ValueError(
                "La fecha inicial no puede ser nula"
            )

        if (
            "active" in update_data
            and update_data["active"] is None
        ):
            raise ValueError(
                "El estado activo no puede ser nulo"
            )

        # ========================================================
        # NORMALIZAR SOURCE REFERENCE
        # ========================================================

        if "source_reference" in update_data:
            update_data["source_reference"] = (
                self._clean_optional_text(
                    update_data["source_reference"]
                )
            )

        # ========================================================
        # CALCULAR ESTADO FINAL
        # ========================================================

        final_valid_from = update_data.get(
            "valid_from",
            price.valid_from,
        )

        final_valid_until = (
            update_data["valid_until"]
            if "valid_until" in update_data
            else price.valid_until
        )

        final_active = update_data.get(
            "active",
            price.active,
        )

        self._validate_dates(
            valid_from=final_valid_from,
            valid_until=final_valid_until,
        )

        # ========================================================
        # SI EL PRECIO QUEDA ACTIVO, VALIDAR CRUCES
        # ========================================================

        if final_active:

            overlapping = (
                await self.repository.find_overlapping(
                    variant_id=price.variant_id,
                    price_list_id=price.price_list_id,
                    valid_from=final_valid_from,
                    valid_until=final_valid_until,
                    exclude_price_id=price.id,
                )
            )

            if overlapping:
                raise ValueError(
                    "La vigencia indicada se cruza con otro precio activo"
                )

        try:
            price = await self.repository.update(
                price=price,
                data=update_data,
            )

            await self.db.commit()
            await self.db.refresh(price)

            return price

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar el precio porque su vigencia entra en conflicto con otro precio existente"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR PRECIO
    # ============================================================

    async def deactivate(
        self,
        price_id: uuid.UUID,
    ) -> VariantPrice:

        price = await self.repository.find_by_id(
            price_id
        )

        if price is None:
            raise LookupError(
                "El precio no existe"
            )

        if not price.active:
            return price

        try:
            price = await self.repository.update(
                price=price,
                data={
                    "active": False
                },
            )

            await self.db.commit()
            await self.db.refresh(price)

            return price

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR EXISTENCIA DE VARIANTE
    # ============================================================

    async def _validate_variant_exists(
        self,
        variant_id: uuid.UUID,
    ):
        variant = await self.variant_repository.find_by_id(
            variant_id
        )

        if variant is None:
            raise ValueError(
                "La variante seleccionada no existe"
            )

        return variant

    # ============================================================
    # VALIDAR VARIANTE ACTIVA
    # ============================================================

    async def _validate_active_variant(
        self,
        variant_id: uuid.UUID,
    ):
        variant = await self._validate_variant_exists(
            variant_id
        )

        if not variant.active:
            raise ValueError(
                "La variante seleccionada está inactiva"
            )

        return variant

    # ============================================================
    # VALIDAR EXISTENCIA DE LISTA DE PRECIOS
    # ============================================================

    async def _validate_price_list_exists(
        self,
        price_list_id: uuid.UUID,
    ):
        price_list = (
            await self.price_list_repository.find_by_id(
                price_list_id
            )
        )

        if price_list is None:
            raise ValueError(
                "La lista de precios seleccionada no existe"
            )

        return price_list

    # ============================================================
    # VALIDAR LISTA DE PRECIOS ACTIVA
    # ============================================================

    async def _validate_active_price_list(
        self,
        price_list_id: uuid.UUID,
    ):
        price_list = (
            await self._validate_price_list_exists(
                price_list_id
            )
        )

        if not price_list.active:
            raise ValueError(
                "La lista de precios seleccionada está inactiva"
            )

        return price_list

    # ============================================================
    # VALIDAR FECHAS
    # ============================================================

    @staticmethod
    def _validate_dates(
        valid_from: date,
        valid_until: date | None,
    ) -> None:

        if (
            valid_until is not None
            and valid_until < valid_from
        ):
            raise ValueError(
                "La fecha final no puede ser anterior a la fecha inicial"
            )

    # ============================================================
    # NORMALIZAR TEXTO OPCIONAL
    # ============================================================

    @staticmethod
    def _clean_optional_text(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None
