import uuid

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.colors.model import Color
from app.modules.colors.repository import ColorRepository
from app.modules.colors.schemas import (
    ColorCreate,
    ColorUpdate,
)


class ColorService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ColorRepository(db)

    # ============================================================
    # LISTAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
    ) -> list[Color]:

        return await self.repository.find_all(
            active=active
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        color_id: uuid.UUID,
    ) -> Color:

        color = await self.repository.find_by_id(
            color_id
        )

        if color is None:
            raise LookupError(
                "El color no existe"
            )

        return color

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: ColorCreate,
    ) -> Color:

        name = data.name.strip()

        generated_slug = slugify(name)

        existing_color = (
            await self.repository.find_by_slug(
                generated_slug
            )
        )

        if existing_color is not None:
            raise ValueError(
                "Ya existe un color con ese nombre"
            )

        try:
            color = await self.repository.create(
                name=name,
                slug=generated_slug,
                hex_code=data.hex_code,
            )

            await self.db.commit()
            await self.db.refresh(color)

            return color

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        color_id: uuid.UUID,
        data: ColorUpdate,
    ) -> Color:

        color = await self.repository.find_by_id(
            color_id
        )

        if color is None:
            raise LookupError(
                "El color no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ========================================================
        # SI CAMBIA EL NOMBRE
        # REGENERAMOS EL SLUG
        # ========================================================

        if "name" in update_data:
            name = update_data["name"].strip()

            generated_slug = slugify(name)

            existing_color = (
                await self.repository.find_by_slug(
                    generated_slug
                )
            )

            if (
                existing_color is not None
                and existing_color.id != color.id
            ):
                raise ValueError(
                    "Ya existe un color con ese nombre"
                )

            update_data["name"] = name
            update_data["slug"] = generated_slug

        try:
            color = await self.repository.update(
                color,
                update_data,
            )

            await self.db.commit()
            await self.db.refresh(color)

            return color

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    # ============================================================

    async def deactivate(
        self,
        color_id: uuid.UUID,
    ) -> Color:

        color = await self.repository.find_by_id(
            color_id
        )

        if color is None:
            raise LookupError(
                "El color no existe"
            )

        if not color.active:
            return color

        try:
            color = await self.repository.update(
                color,
                {
                    "active": False
                },
            )

            await self.db.commit()
            await self.db.refresh(color)

            return color

        except Exception:
            await self.db.rollback()
            raise
