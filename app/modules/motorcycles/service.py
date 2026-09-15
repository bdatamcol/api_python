import uuid

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.brands.repository import BrandRepository
from app.modules.categories.repository import CategoryRepository

from app.modules.motorcycles.model import MotorcycleModel
from app.modules.motorcycles.repository import MotorcycleRepository
from app.modules.motorcycles.schemas import (
    MotorcycleCreate,
    MotorcycleUpdate,
)


class MotorcycleService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = MotorcycleRepository(db)
        self.brand_repository = BrandRepository(db)
        self.category_repository = CategoryRepository(db)

    # ============================================================
    # LISTAR / FILTRAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        brand_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> list[MotorcycleModel]:

        return await self.repository.find_all(
            active=active,
            brand_id=brand_id,
            category_id=category_id,
            search=search,
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        motorcycle_id: uuid.UUID,
    ) -> MotorcycleModel:

        motorcycle = await self.repository.find_by_id(
            motorcycle_id
        )

        if motorcycle is None:
            raise LookupError(
                "La motocicleta no existe"
            )

        return motorcycle

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: MotorcycleCreate,
    ) -> MotorcycleModel:

        # ========================================================
        # VALIDAR MARCA
        # ========================================================

        brand = await self.brand_repository.find_by_id(
            data.brand_id
        )

        if brand is None:
            raise ValueError(
                "La marca seleccionada no existe"
            )

        if not brand.active:
            raise ValueError(
                "La marca seleccionada está inactiva"
            )

        # ========================================================
        # VALIDAR CATEGORIA
        # ========================================================

        if data.category_id is not None:

            category = (
                await self.category_repository.find_by_id(
                    data.category_id
                )
            )

            if category is None:
                raise ValueError(
                    "La categoría seleccionada no existe"
                )

            if not category.active:
                raise ValueError(
                    "La categoría seleccionada está inactiva"
                )

        # ========================================================
        # NORMALIZAR DATOS
        # ========================================================

        name = data.name.strip()

        short_description = (
            data.short_description.strip()
            if data.short_description
            else None
        )

        description = (
            data.description.strip()
            if data.description
            else None
        )

        # ========================================================
        # VALIDAR MODELO DUPLICADO EN LA MARCA
        # ========================================================

        existing_model = (
            await self.repository.find_by_name_and_brand(
                name=name,
                brand_id=data.brand_id,
            )
        )

        if existing_model is not None:
            raise ValueError(
                "Ya existe una motocicleta con ese nombre en la marca seleccionada"
            )

        # ========================================================
        # GENERAR SLUG
        #
        # Ej:
        # victory + SWITCH 125
        # ↓
        # victory-switch-125
        # ========================================================

        generated_slug = (
            f"{brand.slug}-{slugify(name)}"
        )

        existing_slug = (
            await self.repository.find_by_slug(
                generated_slug
            )
        )

        if existing_slug is not None:
            raise ValueError(
                "Ya existe una motocicleta con ese identificador"
            )

        try:
            motorcycle = await self.repository.create(
                brand_id=data.brand_id,
                category_id=data.category_id,
                name=name,
                slug=generated_slug,
                short_description=short_description,
                description=description,
                engine_cc=data.engine_cc,
            )

            await self.db.commit()
            await self.db.refresh(motorcycle)

            return motorcycle

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        motorcycle_id: uuid.UUID,
        data: MotorcycleUpdate,
    ) -> MotorcycleModel:

        motorcycle = await self.repository.find_by_id(
            motorcycle_id
        )

        if motorcycle is None:
            raise LookupError(
                "La motocicleta no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ========================================================
        # DETERMINAR MARCA FINAL
        # ========================================================

        final_brand_id = (
            update_data["brand_id"]
            if "brand_id" in update_data
            else motorcycle.brand_id
        )

        brand = await self.brand_repository.find_by_id(
            final_brand_id
        )

        if brand is None:
            raise ValueError(
                "La marca seleccionada no existe"
            )

        if not brand.active:
            raise ValueError(
                "La marca seleccionada está inactiva"
            )

        # ========================================================
        # VALIDAR CATEGORIA SI CAMBIA
        # ========================================================

        if (
            "category_id" in update_data
            and update_data["category_id"] is not None
        ):

            category = (
                await self.category_repository.find_by_id(
                    update_data["category_id"]
                )
            )

            if category is None:
                raise ValueError(
                    "La categoría seleccionada no existe"
                )

            if not category.active:
                raise ValueError(
                    "La categoría seleccionada está inactiva"
                )

        # ========================================================
        # NOMBRE FINAL
        # ========================================================

        final_name = (
            update_data["name"].strip()
            if "name" in update_data
            else motorcycle.name
        )

        if "name" in update_data:
            update_data["name"] = final_name

        # ========================================================
        # VALIDAR DUPLICADO POR MARCA + NOMBRE
        # ========================================================

        existing_model = (
            await self.repository.find_by_name_and_brand(
                name=final_name,
                brand_id=final_brand_id,
            )
        )

        if (
            existing_model is not None
            and existing_model.id != motorcycle.id
        ):
            raise ValueError(
                "Ya existe una motocicleta con ese nombre en la marca seleccionada"
            )

        # ========================================================
        # REGENERAR SLUG SI CAMBIA NOMBRE O MARCA
        # ========================================================

        if (
            "name" in update_data
            or "brand_id" in update_data
        ):

            generated_slug = (
                f"{brand.slug}-{slugify(final_name)}"
            )

            existing_slug = (
                await self.repository.find_by_slug(
                    generated_slug
                )
            )

            if (
                existing_slug is not None
                and existing_slug.id != motorcycle.id
            ):
                raise ValueError(
                    "Ya existe una motocicleta con ese identificador"
                )

            update_data["slug"] = generated_slug

        # ========================================================
        # NORMALIZAR DESCRIPCION CORTA
        # ========================================================

        if "short_description" in update_data:

            value = update_data["short_description"]

            update_data["short_description"] = (
                value.strip()
                if value
                else None
            )

        # ========================================================
        # NORMALIZAR DESCRIPCION
        # ========================================================

        if "description" in update_data:

            value = update_data["description"]

            update_data["description"] = (
                value.strip()
                if value
                else None
            )

        try:
            motorcycle = await self.repository.update(
                motorcycle,
                update_data,
            )

            await self.db.commit()
            await self.db.refresh(motorcycle)

            return motorcycle

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    # ============================================================

    async def deactivate(
        self,
        motorcycle_id: uuid.UUID,
    ) -> MotorcycleModel:

        motorcycle = await self.repository.find_by_id(
            motorcycle_id
        )

        if motorcycle is None:
            raise LookupError(
                "La motocicleta no existe"
            )

        if not motorcycle.active:
            return motorcycle

        try:
            motorcycle = await self.repository.update(
                motorcycle,
                {
                    "active": False
                },
            )

            await self.db.commit()
            await self.db.refresh(motorcycle)

            return motorcycle

        except Exception:
            await self.db.rollback()
            raise
