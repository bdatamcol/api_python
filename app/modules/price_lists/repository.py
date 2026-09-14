import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.price_lists.model import PriceList


class PriceListRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR LISTAS DE PRECIOS
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        territory_id: uuid.UUID | None = None,
        store_id: uuid.UUID | None = None,
    ) -> list[PriceList]:

        query = select(PriceList)

        if active is not None:
            query = query.where(
                PriceList.active == active
            )

        if territory_id is not None:
            query = query.where(
                PriceList.territory_id == territory_id
            )

        if store_id is not None:
            query = query.where(
                PriceList.store_id == store_id
            )

        query = query.order_by(
            PriceList.priority.asc(),
            PriceList.name.asc(),
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
        price_list_id: uuid.UUID,
    ) -> PriceList | None:

        query = select(PriceList).where(
            PriceList.id == price_list_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR CODIGO
    # ============================================================

    async def find_by_code(
        self,
        code: str,
    ) -> PriceList | None:

        query = select(PriceList).where(
            PriceList.code == code
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR TERRITORIO
    # ============================================================

    async def find_by_territory(
        self,
        territory_id: uuid.UUID,
        active: bool | None = True,
    ) -> list[PriceList]:

        query = select(PriceList).where(
            PriceList.territory_id == territory_id
        )

        if active is not None:
            query = query.where(
                PriceList.active == active
            )

        query = query.order_by(
            PriceList.priority.asc()
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR POR SEDE
    # ============================================================

    async def find_by_store(
        self,
        store_id: uuid.UUID,
        active: bool | None = True,
    ) -> list[PriceList]:

        query = select(PriceList).where(
            PriceList.store_id == store_id
        )

        if active is not None:
            query = query.where(
                PriceList.active == active
            )

        query = query.order_by(
            PriceList.priority.asc()
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # BUSCAR LISTAS GENERALES
    #
    # territory_id = NULL
    # store_id = NULL
    # ============================================================

    async def find_global(
        self,
        active: bool | None = True,
    ) -> list[PriceList]:

        query = select(PriceList).where(
            PriceList.territory_id.is_(None),
            PriceList.store_id.is_(None),
        )

        if active is not None:
            query = query.where(
                PriceList.active == active
            )

        query = query.order_by(
            PriceList.priority.asc()
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
        name: str,
        code: str,
        territory_id: uuid.UUID | None = None,
        store_id: uuid.UUID | None = None,
        currency: str = "COP",
        priority: int = 100,
        source_system: str = "MANUAL",
    ) -> PriceList:

        price_list = PriceList(
            name=name,
            code=code,
            territory_id=territory_id,
            store_id=store_id,
            currency=currency,
            priority=priority,
            source_system=source_system,
        )

        self.db.add(price_list)

        await self.db.flush()
        await self.db.refresh(price_list)

        return price_list

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        price_list: PriceList,
        data: dict,
    ) -> PriceList:

        for field, value in data.items():
            setattr(
                price_list,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(price_list)

        return price_list
