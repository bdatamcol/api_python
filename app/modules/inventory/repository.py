import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.model import Inventory


class InventoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # BUSCAR INVENTARIO POR ID
    # ============================================================

    async def find_by_id(
        self,
        inventory_id: uuid.UUID,
    ) -> Inventory | None:

        query = select(Inventory).where(
            Inventory.id == inventory_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR VARIANTE + TIENDA
    # ============================================================

    async def find_by_variant_store(
        self,
        variant_id: uuid.UUID,
        store_id: uuid.UUID,
    ) -> Inventory | None:

        query = select(Inventory).where(
            Inventory.variant_id == variant_id,
            Inventory.store_id == store_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # LISTAR INVENTARIO DE UNA VARIANTE
    # ============================================================

    async def find_all_by_variant(
        self,
        variant_id: uuid.UUID,
    ) -> list[Inventory]:

        query = (
            select(Inventory)
            .where(
                Inventory.variant_id == variant_id
            )
            .order_by(
                Inventory.available_quantity.desc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR INVENTARIO DE UNA TIENDA
    # ============================================================

    async def find_all_by_store(
        self,
        store_id: uuid.UUID,
    ) -> list[Inventory]:

        query = (
            select(Inventory)
            .where(
                Inventory.store_id == store_id
            )
            .order_by(
                Inventory.available_quantity.desc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # LISTAR SOLO INVENTARIO DISPONIBLE DE UNA VARIANTE
    # ============================================================

    async def find_available_by_variant(
        self,
        variant_id: uuid.UUID,
    ) -> list[Inventory]:

        query = (
            select(Inventory)
            .where(
                Inventory.variant_id == variant_id,
                Inventory.available_quantity > 0,
            )
            .order_by(
                Inventory.available_quantity.desc()
            )
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        variant_id: uuid.UUID,
        store_id: uuid.UUID,
        quantity: int,
        reserved_quantity: int,
    ) -> Inventory:

        inventory = Inventory(
            variant_id=variant_id,
            store_id=store_id,
            quantity=quantity,
            reserved_quantity=reserved_quantity,
        )

        self.db.add(inventory)

        await self.db.flush()
        await self.db.refresh(inventory)

        return inventory

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        inventory: Inventory,
        data: dict,
    ) -> Inventory:

        for field, value in data.items():
            setattr(
                inventory,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(inventory)

        return inventory
