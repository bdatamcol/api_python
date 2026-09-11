import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.brands.model import Brand


class BrandRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR MARCAS
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[Brand]:

        query = select(Brand)

        if active is not None:
            query = query.where(
                Brand.active == active
            )

        query = query.order_by(
            Brand.name.asc()
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
        brand_id: uuid.UUID,
    ) -> Brand | None:

        query = select(Brand).where(
            Brand.id == brand_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE
    # ============================================================

    async def find_by_name(
        self,
        name: str,
    ) -> Brand | None:

        query = select(Brand).where(
            Brand.name == name
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR SLUG
    # ============================================================

    async def find_by_slug(
        self,
        slug: str,
    ) -> Brand | None:

        query = select(Brand).where(
            Brand.slug == slug
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
    ) -> Brand:

        brand = Brand(
            name=name,
            slug=slug,
        )

        self.db.add(brand)

        await self.db.flush()
        await self.db.refresh(brand)

        return brand

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        brand: Brand,
        data: dict,
    ) -> Brand:

        for field, value in data.items():
            setattr(
                brand,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(brand)

        return brand
