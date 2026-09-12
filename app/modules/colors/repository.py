import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.colors.model import Color


class ColorRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR COLORES
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[Color]:

        query = select(Color)

        if active is not None:
            query = query.where(
                Color.active == active
            )

        query = query.order_by(
            Color.name.asc()
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
        color_id: uuid.UUID,
    ) -> Color | None:

        query = select(Color).where(
            Color.id == color_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE
    # ============================================================

    async def find_by_name(
        self,
        name: str,
    ) -> Color | None:

        query = select(Color).where(
            Color.name == name
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR SLUG
    # ============================================================

    async def find_by_slug(
        self,
        slug: str,
    ) -> Color | None:

        query = select(Color).where(
            Color.slug == slug
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        name: str,
        slug: str,
        hex_code: str | None = None,
    ) -> Color:

        color = Color(
            name=name,
            slug=slug,
            hex_code=hex_code,
        )

        self.db.add(color)

        await self.db.flush()
        await self.db.refresh(color)

        return color

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        color: Color,
        data: dict,
    ) -> Color:

        for field, value in data.items():
            setattr(
                color,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(color)

        return color
