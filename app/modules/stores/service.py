import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.stores.model import Store
from app.modules.stores.repository import StoreRepository
from app.modules.stores.schemas import (
    StoreCreate,
    StoreUpdate,
)

from app.modules.territories.repository import TerritoryRepository
from app.modules.territories.schemas import TerritoryType


class StoreService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = StoreRepository(db)
        self.territory_repository = TerritoryRepository(db)

    # ============================================================
    # LISTAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        territory_id: uuid.UUID | None = None,
    ) -> list[Store]:

        return await self.repository.find_all(
            active=active,
            territory_id=territory_id,
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        store_id: uuid.UUID,
    ) -> Store:

        store = await self.repository.find_by_id(
            store_id
        )

        if store is None:
            raise LookupError(
                "La sede no existe"
            )

        return store

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: StoreCreate,
    ) -> Store:

        name = data.name.strip()

        code = data.code.strip().upper()

        address = (
            data.address.strip()
            if data.address
            else None
        )

        # ========================================================
        # VALIDAR TERRITORIO
        # ========================================================

        await self._validate_territory(
            data.territory_id
        )

        # ========================================================
        # VALIDAR CODIGO UNICO
        # ========================================================

        existing_code = (
            await self.repository.find_by_code(
                code
            )
        )

        if existing_code is not None:
            raise ValueError(
                "Ya existe una sede con ese código"
            )

        # ========================================================
        # VALIDAR NOMBRE DENTRO DEL TERRITORIO
        # ========================================================

        existing_name = (
            await self.repository.find_by_name_and_territory(
                name=name,
                territory_id=data.territory_id,
            )
        )

        if existing_name is not None:
            raise ValueError(
                "Ya existe una sede con ese nombre en el territorio seleccionado"
            )

        try:
            store = await self.repository.create(
                territory_id=data.territory_id,
                name=name,
                code=code,
                address=address,
            )

            await self.db.commit()
            await self.db.refresh(store)

            return store

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        store_id: uuid.UUID,
        data: StoreUpdate,
    ) -> Store:

        store = await self.repository.find_by_id(
            store_id
        )

        if store is None:
            raise LookupError(
                "La sede no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ========================================================
        # TERRITORIO FINAL
        # ========================================================

        final_territory_id = (
            update_data["territory_id"]
            if "territory_id" in update_data
            else store.territory_id
        )

        await self._validate_territory(
            final_territory_id
        )

        # ========================================================
        # NORMALIZAR NOMBRE
        # ========================================================

        final_name = (
            update_data["name"].strip()
            if "name" in update_data
            else store.name
        )

        if "name" in update_data:
            update_data["name"] = final_name

        # ========================================================
        # VALIDAR NOMBRE DUPLICADO
        # ========================================================

        existing_name = (
            await self.repository.find_by_name_and_territory(
                name=final_name,
                territory_id=final_territory_id,
            )
        )

        if (
            existing_name is not None
            and existing_name.id != store.id
        ):
            raise ValueError(
                "Ya existe una sede con ese nombre en el territorio seleccionado"
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
                and existing_code.id != store.id
            ):
                raise ValueError(
                    "Ya existe una sede con ese código"
                )

            update_data["code"] = code

        # ========================================================
        # NORMALIZAR DIRECCION
        # ========================================================

        if "address" in update_data:

            address = update_data["address"]

            update_data["address"] = (
                address.strip()
                if address
                else None
            )

        try:
            store = await self.repository.update(
                store,
                update_data,
            )

            await self.db.commit()
            await self.db.refresh(store)

            return store

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    # ============================================================

    async def deactivate(
        self,
        store_id: uuid.UUID,
    ) -> Store:

        store = await self.repository.find_by_id(
            store_id
        )

        if store is None:
            raise LookupError(
                "La sede no existe"
            )

        if not store.active:
            return store

        try:
            store = await self.repository.update(
                store,
                {
                    "active": False
                },
            )

            await self.db.commit()
            await self.db.refresh(store)

            return store

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR TERRITORIO DE LA SEDE
    # ============================================================

    async def _validate_territory(
        self,
        territory_id: uuid.UUID,
    ) -> None:

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

        territory_type = TerritoryType(
            territory.type
        )

        if territory_type not in (
            TerritoryType.CITY,
            TerritoryType.ZONE,
        ):
            raise ValueError(
                "Una sede debe pertenecer a una ciudad o zona"
            )
