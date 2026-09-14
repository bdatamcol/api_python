import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.stores.model import Store


class StoreRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR SEDES
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        territory_id: uuid.UUID | None = None,
    ) -> list[Store]:

        query = select(Store)

        if active is not None:
            query = query.where(
                Store.active == active
            )

        if territory_id is not None:
            query = query.where(
                Store.territory_id == territory_id
            )

        query = query.order_by(
            Store.name.asc()
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        store_id: uuid.UUID,
    ) -> Store | None:

        query = select(Store).where(
            Store.id == store_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR CODIGO
    # ============================================================

    async def find_by_code(
        self,
        code: str,
    ) -> Store | None:

        query = select(Store).where(
            Store.code == code
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE DENTRO DE UN TERRITORIO
    # ============================================================

    async def find_by_name_and_territory(
        self,
        name: str,
        territory_id: uuid.UUID,
    ) -> Store | None:

        query = select(Store).where(
            Store.name == name,
            Store.territory_id == territory_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        territory_id: uuid.UUID,
        name: str,
        code: str,
        address: str | None = None,
    ) -> Store:

        store = Store(
            territory_id=territory_id,
            name=name,
            code=code,
            address=address,
        )

        self.db.add(store)

        await self.db.flush()
        await self.db.refresh(store)

        return store

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        store: Store,
        data: dict,
    ) -> Store:

        for field, value in data.items():
            setattr(
                store,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(store)

        return store
