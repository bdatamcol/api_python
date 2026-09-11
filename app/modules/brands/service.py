import uuid

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.brands.model import Brand
from app.modules.brands.repository import BrandRepository
from app.modules.brands.schemas import BrandCreate, BrandUpdate


class BrandService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BrandRepository(db)

    # ============================================================
    # LISTAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[Brand]:

        return await self.repository.find_all(
            active=active
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        brand_id: uuid.UUID,
    ) -> Brand:

        brand = await self.repository.find_by_id(
            brand_id
        )

        if brand is None:
            raise LookupError(
                "La marca no existe"
            )

        return brand

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: BrandCreate,
    ) -> Brand:

        name = data.name.strip()

        generated_slug = slugify(name)

        existing_brand = (
            await self.repository.find_by_slug(
                generated_slug
            )
        )

        if existing_brand is not None:
            raise ValueError(
                "Ya existe una marca con ese nombre"
            )

        try:
            brand = await self.repository.create(
                name=name,
                slug=generated_slug,
            )

            await self.db.commit()

            await self.db.refresh(brand)

            return brand

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        brand_id: uuid.UUID,
        data: BrandUpdate,
    ) -> Brand:

        brand = await self.repository.find_by_id(
            brand_id
        )

        if brand is None:
            raise LookupError(
                "La marca no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # Si cambia el nombre,
        # también regeneramos el slug.
        if "name" in update_data:

            name = update_data["name"].strip()

            generated_slug = slugify(name)

            existing_brand = (
                await self.repository.find_by_slug(
                    generated_slug
                )
            )

            if (
                existing_brand is not None
                and existing_brand.id != brand.id
            ):
                raise ValueError(
                    "Ya existe una marca con ese nombre"
                )

            update_data["name"] = name
            update_data["slug"] = generated_slug

        try:
            brand = await self.repository.update(
                brand,
                update_data,
            )

            await self.db.commit()

            await self.db.refresh(brand)

            return brand

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    # ============================================================

    async def deactivate(
        self,
        brand_id: uuid.UUID,
    ) -> Brand:

        brand = await self.repository.find_by_id(
            brand_id
        )

        if brand is None:
            raise LookupError(
                "La marca no existe"
            )

        if not brand.active:
            return brand

        try:
            brand = await self.repository.update(
                brand,
                {
                    "active": False
                },
            )

            await self.db.commit()

            await self.db.refresh(brand)

            return brand

        except Exception:
            await self.db.rollback()
            raise
