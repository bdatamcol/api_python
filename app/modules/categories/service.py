import uuid

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.model import MotorcycleCategory
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryUpdate,
)


class CategoryService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CategoryRepository(db)

    # ============================================================
    # LISTAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[MotorcycleCategory]:

        return await self.repository.find_all(
            active=active
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        category_id: uuid.UUID,
    ) -> MotorcycleCategory:

        category = await self.repository.find_by_id(
            category_id
        )

        if category is None:
            raise LookupError(
                "La categoría no existe"
            )

        return category

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: CategoryCreate,
    ) -> MotorcycleCategory:

        name = data.name.strip()

        generated_slug = slugify(name)

        existing_category = (
            await self.repository.find_by_slug(
                generated_slug
            )
        )

        if existing_category is not None:
            raise ValueError(
                "Ya existe una categoría con ese nombre"
            )

        description = (
            data.description.strip()
            if data.description
            else None
        )

        try:
            category = await self.repository.create(
                name=name,
                slug=generated_slug,
                description=description,
            )

            await self.db.commit()

            await self.db.refresh(category)

            return category

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        category_id: uuid.UUID,
        data: CategoryUpdate,
    ) -> MotorcycleCategory:

        category = await self.repository.find_by_id(
            category_id
        )

        if category is None:
            raise LookupError(
                "La categoría no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ========================================================
        # SI CAMBIA EL NOMBRE
        # REGENERAR SLUG Y VALIDAR DUPLICADOS
        # ========================================================

        if "name" in update_data:

            name = update_data["name"].strip()

            generated_slug = slugify(name)

            existing_category = (
                await self.repository.find_by_slug(
                    generated_slug
                )
            )

            if (
                existing_category is not None
                and existing_category.id != category.id
            ):
                raise ValueError(
                    "Ya existe una categoría con ese nombre"
                )

            update_data["name"] = name
            update_data["slug"] = generated_slug

        # ========================================================
        # LIMPIAR DESCRIPTION
        # ========================================================

        if "description" in update_data:

            description = update_data["description"]

            update_data["description"] = (
                description.strip()
                if description
                else None
            )

        try:
            category = await self.repository.update(
                category,
                update_data,
            )

            await self.db.commit()

            await self.db.refresh(category)

            return category

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    # ============================================================

    async def deactivate(
        self,
        category_id: uuid.UUID,
    ) -> MotorcycleCategory:

        category = await self.repository.find_by_id(
            category_id
        )

        if category is None:
            raise LookupError(
                "La categoría no existe"
            )

        if not category.active:
            return category

        try:
            category = await self.repository.update(
                category,
                {
                    "active": False
                },
            )

            await self.db.commit()

            await self.db.refresh(category)

            return category

        except Exception:
            await self.db.rollback()
            raise
