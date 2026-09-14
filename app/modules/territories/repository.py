import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.territories.model import Territory
from app.modules.territories.schemas import TerritoryType


class TerritoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR TERRITORIOS
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        territory_type: TerritoryType | None = None,
        parent_id: uuid.UUID | None = None,
    ) -> list[Territory]:

        query = select(Territory)

        if active is not None:
            query = query.where(
                Territory.active == active
            )

        if territory_type is not None:
            query = query.where(
                Territory.type == territory_type.value
            )

        if parent_id is not None:
            query = query.where(
                Territory.parent_id == parent_id
            )

        query = query.order_by(
            Territory.name.asc()
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
        territory_id: uuid.UUID,
    ) -> Territory | None:

        query = select(Territory).where(
            Territory.id == territory_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR CODIGO
    # ============================================================

    async def find_by_code(
        self,
        code: str,
    ) -> Territory | None:

        query = select(Territory).where(
            Territory.code == code
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE Y PADRE
    # ============================================================

    async def find_by_name_and_parent(
        self,
        name: str,
        parent_id: uuid.UUID | None,
    ) -> Territory | None:

        query = select(Territory).where(
            Territory.name == name
        )

        if parent_id is None:
            query = query.where(
                Territory.parent_id.is_(None)
            )
        else:
            query = query.where(
                Territory.parent_id == parent_id
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # OBTENER HIJOS DIRECTOS
    # ============================================================

    async def find_children(
        self,
        parent_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[Territory]:

        query = select(Territory).where(
            Territory.parent_id == parent_id
        )

        if active is not None:
            query = query.where(
                Territory.active == active
            )

        query = query.order_by(
            Territory.name.asc()
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
        territory_type: TerritoryType,
        parent_id: uuid.UUID | None = None,
        code: str | None = None,
    ) -> Territory:

        territory = Territory(
            name=name,
            type=territory_type.value,
            parent_id=parent_id,
            code=code,
        )

        self.db.add(territory)

        await self.db.flush()
        await self.db.refresh(territory)

        return territory

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        territory: Territory,
        data: dict,
    ) -> Territory:

        if "type" in data and isinstance(
            data["type"],
            TerritoryType,
        ):
            data["type"] = data["type"].value

        for field, value in data.items():
            setattr(
                territory,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(territory)

        return territory
