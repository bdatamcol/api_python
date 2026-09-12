import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.model import MotorcycleCategory


class CategoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR CATEGORIAS
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[MotorcycleCategory]:

        query = select(MotorcycleCategory)

        if active is not None:
            query = query.where(
                MotorcycleCategory.active == active
            )

        query = query.order_by(
            MotorcycleCategory.name.asc()
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
        category_id: uuid.UUID,
    ) -> MotorcycleCategory | None:

        query = select(MotorcycleCategory).where(
            MotorcycleCategory.id == category_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE
    # ============================================================

    async def find_by_name(
        self,
        name: str,
    ) -> MotorcycleCategory | None:

        query = select(MotorcycleCategory).where(
            MotorcycleCategory.name == name
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR SLUG
    # ============================================================

    async def find_by_slug(
        self,
        slug: str,
    ) -> MotorcycleCategory | None:

        query = select(MotorcycleCategory).where(
            MotorcycleCategory.slug == slug
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
        description: str | None = None,
    ) -> MotorcycleCategory:

        category = MotorcycleCategory(
            name=name,
            slug=slug,
            description=description,
        )

        self.db.add(category)

        await self.db.flush()
        await self.db.refresh(category)

        return category

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        category: MotorcycleCategory,
        data: dict,
    ) -> MotorcycleCategory:

        for field, value in data.items():
            setattr(
                category,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(category)

        return category
