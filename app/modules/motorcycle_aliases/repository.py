import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motorcycle_aliases.model import MotorcycleAlias


class MotorcycleAliasRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # LISTAR ALIAS DE UNA MOTOCICLETA
    # ============================================================

    async def find_all_by_model(
        self,
        model_id: uuid.UUID,
    ) -> list[MotorcycleAlias]:

        query = (
            select(MotorcycleAlias)
            .where(
                MotorcycleAlias.model_id == model_id
            )
            .order_by(
                MotorcycleAlias.alias.asc()
            )
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
        alias_id: uuid.UUID,
    ) -> MotorcycleAlias | None:

        query = select(MotorcycleAlias).where(
            MotorcycleAlias.id == alias_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # BUSCAR ALIAS NORMALIZADO DENTRO DE UNA MOTO
    #
    # Ejemplo:
    #
    # model_id = SWITCH 125
    # normalized_alias = "victory switch"
    # ============================================================

    async def find_by_normalized_alias(
        self,
        model_id: uuid.UUID,
        normalized_alias: str,
    ) -> MotorcycleAlias | None:

        query = select(MotorcycleAlias).where(
            MotorcycleAlias.model_id == model_id,
            MotorcycleAlias.normalized_alias == normalized_alias,
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        model_id: uuid.UUID,
        alias: str,
        normalized_alias: str,
    ) -> MotorcycleAlias:

        motorcycle_alias = MotorcycleAlias(
            model_id=model_id,
            alias=alias,
            normalized_alias=normalized_alias,
        )

        self.db.add(motorcycle_alias)

        await self.db.flush()
        await self.db.refresh(motorcycle_alias)

        return motorcycle_alias

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        motorcycle_alias: MotorcycleAlias,
        alias: str,
        normalized_alias: str,
    ) -> MotorcycleAlias:

        motorcycle_alias.alias = alias
        motorcycle_alias.normalized_alias = normalized_alias

        await self.db.flush()
        await self.db.refresh(motorcycle_alias)

        return motorcycle_alias

    # ============================================================
    # ELIMINAR
    #
    # En alias sí podemos hacer borrado físico.
    # No representa información histórica importante.
    # ============================================================

    async def delete(
        self,
        motorcycle_alias: MotorcycleAlias,
    ) -> None:

        await self.db.delete(
            motorcycle_alias
        )

        await self.db.flush()
