import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.model import Inventory
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import (
    InventoryCreateForVariant,
    InventoryUpdate,
)
from app.modules.motorcycle_variants.repository import (
    MotorcycleVariantRepository,
)
from app.modules.stores.repository import StoreRepository


class InventoryService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = InventoryRepository(db)
        self.variant_repository = MotorcycleVariantRepository(db)
        self.store_repository = StoreRepository(db)

    # ============================================================
    # BUSCAR INVENTARIO POR ID
    # ============================================================

    async def find_by_id(
        self,
        inventory_id: uuid.UUID,
    ) -> Inventory:

        inventory = await self.repository.find_by_id(
            inventory_id
        )

        if inventory is None:
            raise LookupError(
                "El registro de inventario no existe"
            )

        return inventory

    # ============================================================
    # LISTAR INVENTARIO DE UNA VARIANTE
    # ============================================================

    async def find_all_by_variant(
        self,
        variant_id: uuid.UUID,
    ) -> list[Inventory]:

        await self._validate_variant_exists(
            variant_id
        )

        return await self.repository.find_all_by_variant(
            variant_id
        )

    # ============================================================
    # LISTAR INVENTARIO DISPONIBLE
    # ============================================================

    async def find_available_by_variant(
        self,
        variant_id: uuid.UUID,
    ) -> list[Inventory]:

        await self._validate_variant_exists(
            variant_id
        )

        return await self.repository.find_available_by_variant(
            variant_id
        )

    # ============================================================
    # LISTAR INVENTARIO DE UNA TIENDA
    # ============================================================

    async def find_all_by_store(
        self,
        store_id: uuid.UUID,
    ) -> list[Inventory]:

        await self._validate_store_exists(
            store_id
        )

        return await self.repository.find_all_by_store(
            store_id
        )

    # ============================================================
    # CREAR INVENTARIO PARA UNA VARIANTE
    # ============================================================

    async def create_for_variant(
        self,
        variant_id: uuid.UUID,
        data: InventoryCreateForVariant,
    ) -> Inventory:

        await self._validate_active_variant(
            variant_id
        )

        await self._validate_active_store(
            data.store_id
        )

        self._validate_quantities(
            quantity=data.quantity,
            reserved_quantity=data.reserved_quantity,
        )

        existing_inventory = (
            await self.repository.find_by_variant_store(
                variant_id=variant_id,
                store_id=data.store_id,
            )
        )

        if existing_inventory is not None:
            raise ValueError(
                "Ya existe un registro de inventario para esta variante en la tienda seleccionada"
            )

        try:
            inventory = await self.repository.create(
                variant_id=variant_id,
                store_id=data.store_id,
                quantity=data.quantity,
                reserved_quantity=data.reserved_quantity,
            )

            await self.db.commit()
            await self.db.refresh(
                inventory
            )

            return inventory

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible crear el inventario. Verifica la variante, la tienda y las cantidades."
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR INVENTARIO
    # ============================================================

    async def update(
        self,
        inventory_id: uuid.UUID,
        data: InventoryUpdate,
    ) -> Inventory:

        inventory = await self.repository.find_by_id(
            inventory_id
        )

        if inventory is None:
            raise LookupError(
                "El registro de inventario no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return inventory

        # ========================================================
        # NO PERMITIR NULL
        # ========================================================

        if (
            "quantity" in update_data
            and update_data["quantity"] is None
        ):
            raise ValueError(
                "La cantidad física no puede ser nula"
            )

        if (
            "reserved_quantity" in update_data
            and update_data["reserved_quantity"] is None
        ):
            raise ValueError(
                "La cantidad reservada no puede ser nula"
            )

        # ========================================================
        # CALCULAR VALORES FINALES
        # ========================================================

        final_quantity = update_data.get(
            "quantity",
            inventory.quantity,
        )

        final_reserved_quantity = update_data.get(
            "reserved_quantity",
            inventory.reserved_quantity,
        )

        self._validate_quantities(
            quantity=final_quantity,
            reserved_quantity=final_reserved_quantity,
        )

        try:
            inventory = await self.repository.update(
                inventory=inventory,
                data=update_data,
            )

            await self.db.commit()
            await self.db.refresh(
                inventory
            )

            return inventory

        except IntegrityError as exc:
            await self.db.rollback()

            raise ValueError(
                "No fue posible actualizar el inventario. Verifica las cantidades."
            ) from exc

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
    # VALIDAR EXISTENCIA DE TIENDA
    # ============================================================

    async def _validate_store_exists(
        self,
        store_id: uuid.UUID,
    ):
        store = await self.store_repository.find_by_id(
            store_id
        )

        if store is None:
            raise ValueError(
                "La tienda seleccionada no existe"
            )

        return store

    # ============================================================
    # VALIDAR TIENDA ACTIVA
    # ============================================================

    async def _validate_active_store(
        self,
        store_id: uuid.UUID,
    ):
        store = await self._validate_store_exists(
            store_id
        )

        if not store.active:
            raise ValueError(
                "La tienda seleccionada está inactiva"
            )

        return store

    # ============================================================
    # VALIDAR CANTIDADES
    # ============================================================

    @staticmethod
    def _validate_quantities(
        quantity: int,
        reserved_quantity: int,
    ) -> None:

        if quantity < 0:
            raise ValueError(
                "La cantidad física no puede ser negativa"
            )

        if reserved_quantity < 0:
            raise ValueError(
                "La cantidad reservada no puede ser negativa"
            )

        if reserved_quantity > quantity:
            raise ValueError(
                "La cantidad reservada no puede ser mayor que la cantidad física"
            )
