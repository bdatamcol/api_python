import uuid
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motorcycles.model import MotorcycleModel


class MotorcycleRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR / FILTRAR MODELOS
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        brand_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> list[MotorcycleModel]:

        query = select(MotorcycleModel)

        if active is not None:
            query = query.where(
                MotorcycleModel.active == active
            )

        if brand_id is not None:
            query = query.where(
                MotorcycleModel.brand_id == brand_id
            )

        if category_id is not None:
            query = query.where(
                MotorcycleModel.category_id == category_id
            )

        if search:
            search_value = f"%{search.strip()}%"

            query = query.where(
                or_(
                    MotorcycleModel.name.ilike(search_value),
                    MotorcycleModel.slug.ilike(search_value),
                    MotorcycleModel.short_description.ilike(
                        search_value
                    ),
                )
            )

        query = query.order_by(
            MotorcycleModel.name.asc()
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
        motorcycle_id: uuid.UUID,
    ) -> MotorcycleModel | None:

        query = select(MotorcycleModel).where(
            MotorcycleModel.id == motorcycle_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR SLUG
    # ============================================================

    async def find_by_slug(
        self,
        slug: str,
    ) -> MotorcycleModel | None:

        query = select(MotorcycleModel).where(
            MotorcycleModel.slug == slug
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR POR NOMBRE Y MARCA
    #
    # Evita tener dos veces:
    #
    # VICTORY + SWITCH 125
    # ============================================================

    async def find_by_name_and_brand(
        self,
        name: str,
        brand_id: uuid.UUID,
    ) -> MotorcycleModel | None:

        query = select(MotorcycleModel).where(
            MotorcycleModel.name == name,
            MotorcycleModel.brand_id == brand_id,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR MODELO
    # ============================================================

    async def create(
        self,
        brand_id: uuid.UUID,
        name: str,
        slug: str,
        category_id: uuid.UUID | None = None,
        short_description: str | None = None,
        description: str | None = None,
        engine_cc: Decimal | None = None,
    ) -> MotorcycleModel:

        motorcycle = MotorcycleModel(
            brand_id=brand_id,
            category_id=category_id,
            name=name,
            slug=slug,
            short_description=short_description,
            description=description,
            engine_cc=engine_cc,
        )

        self.db.add(motorcycle)

        await self.db.flush()
        await self.db.refresh(motorcycle)

        return motorcycle

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        motorcycle: MotorcycleModel,
        data: dict,
    ) -> MotorcycleModel:

        for field, value in data.items():
            setattr(
                motorcycle,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(motorcycle)

        return motorcycle
