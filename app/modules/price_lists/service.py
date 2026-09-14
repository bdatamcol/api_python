import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.price_lists.model import PriceList
from app.modules.price_lists.repository import PriceListRepository
from app.modules.price_lists.schemas import (
    PriceListCreate,
    PriceListUpdate,
)
from app.modules.stores.repository import StoreRepository
from app.modules.territories.repository import TerritoryRepository


class PriceListService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = PriceListRepository(db)
        self.territory_repository = TerritoryRepository(db)
        self.store_repository = StoreRepository(db)

    # ============================================================
    # LISTAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        territory_id: uuid.UUID | None = None,
        store_id: uuid.UUID | None = None,
    ) -> list[PriceList]:

        return await self.repository.find_all(
            active=active,
            territory_id=territory_id,
            store_id=store_id,
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        price_list_id: uuid.UUID,
    ) -> PriceList:

        price_list = await self.repository.find_by_id(
            price_list_id
        )

        if price_list is None:
            raise LookupError(
                "La lista de precios no existe"
            )

        return price_list

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: PriceListCreate,
    ) -> PriceList:

        name = data.name.strip()
        code = data.code.strip().upper()
        currency = data.currency.strip().upper()
        source_system = data.source_system.strip().upper()

        # ========================================================
        # VALIDAR CODIGO UNICO
        # ========================================================

        existing_code = await self.repository.find_by_code(
            code
        )

        if existing_code is not None:
            raise ValueError(
                "Ya existe una lista de precios con ese código"
            )

        # ========================================================
        # VALIDAR UBICACION
        # ========================================================

        await self._validate_location(
            territory_id=data.territory_id,
            store_id=data.store_id,
        )

        try:
            price_list = await self.repository.create(
                name=name,
                code=code,
                territory_id=data.territory_id,
                store_id=data.store_id,
                currency=currency,
                priority=data.priority,
                source_system=source_system,
            )

            await self.db.commit()
            await self.db.refresh(price_list)

            return price_list

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        price_list_id: uuid.UUID,
        data: PriceListUpdate,
    ) -> PriceList:

        price_list = await self.repository.find_by_id(
            price_list_id
        )

        if price_list is None:
            raise LookupError(
                "La lista de precios no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ========================================================
        # NORMALIZAR NOMBRE
        # ========================================================

        if "name" in update_data:
            update_data["name"] = (
                update_data["name"].strip()
            )

        # ========================================================
        # NORMALIZAR Y VALIDAR CODIGO
        # ========================================================

        if "code" in update_data:

            code = update_data["code"].strip().upper()

            existing_code = (
                await self.repository.find_by_code(
                    code
                )
            )

            if (
                existing_code is not None
                and existing_code.id != price_list.id
            ):
                raise ValueError(
                    "Ya existe una lista de precios con ese código"
                )

            update_data["code"] = code

        # ========================================================
        # NORMALIZAR MONEDA
        # ========================================================

        if "currency" in update_data:
            update_data["currency"] = (
                update_data["currency"]
                .strip()
                .upper()
            )

        # ========================================================
        # NORMALIZAR SISTEMA ORIGEN
        # ========================================================

        if "source_system" in update_data:
            update_data["source_system"] = (
                update_data["source_system"]
                .strip()
                .upper()
            )

        # ========================================================
        # CAMBIO ENTRE TERRITORIO Y SEDE
        #
        # Si se asigna una sede, quitamos automáticamente
        # el territorio anterior.
        #
        # Si se asigna un territorio, quitamos automáticamente
        # la sede anterior.
        # ========================================================

        if (
            "store_id" in update_data
            and update_data["store_id"] is not None
        ):
            update_data["territory_id"] = None

        elif (
            "territory_id" in update_data
            and update_data["territory_id"] is not None
        ):
            update_data["store_id"] = None

        # ========================================================
        # CALCULAR UBICACION FINAL
        # ========================================================

        final_territory_id = (
            update_data["territory_id"]
            if "territory_id" in update_data
            else price_list.territory_id
        )

        final_store_id = (
            update_data["store_id"]
            if "store_id" in update_data
            else price_list.store_id
        )

        # ========================================================
        # VALIDAR UBICACION FINAL
        # ========================================================

        await self._validate_location(
            territory_id=final_territory_id,
            store_id=final_store_id,
        )

        try:
            price_list = await self.repository.update(
                price_list,
                update_data,
            )

            await self.db.commit()
            await self.db.refresh(price_list)

            return price_list

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    # ============================================================

    async def deactivate(
        self,
        price_list_id: uuid.UUID,
    ) -> PriceList:

        price_list = await self.repository.find_by_id(
            price_list_id
        )

        if price_list is None:
            raise LookupError(
                "La lista de precios no existe"
            )

        if not price_list.active:
            return price_list

        try:
            price_list = await self.repository.update(
                price_list,
                {
                    "active": False
                },
            )

            await self.db.commit()
            await self.db.refresh(price_list)

            return price_list

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR UBICACION
    # ============================================================

    async def _validate_location(
        self,
        territory_id: uuid.UUID | None,
        store_id: uuid.UUID | None,
    ) -> None:

        # ========================================================
        # NO PUEDEN EXISTIR AMBOS
        # ========================================================

        if (
            territory_id is not None
            and store_id is not None
        ):
            raise ValueError(
                "Una lista de precios no puede pertenecer a un territorio y a una sede al mismo tiempo"
            )

        # ========================================================
        # VALIDAR TERRITORIO
        # ========================================================

        if territory_id is not None:

            territory = (
                await self.territory_repository.find_by_id(
                    territory_id
                )
            )

            if territory is None:
                raise ValueError(
                    "El territorio seleccionado no existe"
                )

            if not territory.active:
                raise ValueError(
                    "El territorio seleccionado está inactivo"
                )

        # ========================================================
        # VALIDAR SEDE
        # ========================================================

        if store_id is not None:

            store = (
                await self.store_repository.find_by_id(
                    store_id
                )
            )

            if store is None:
                raise ValueError(
                    "La sede seleccionada no existe"
                )

            if not store.active:
                raise ValueError(
                    "La sede seleccionada está inactiva"
                )
