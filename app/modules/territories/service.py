import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.territories.model import Territory
from app.modules.territories.repository import TerritoryRepository
from app.modules.territories.schemas import (
    TerritoryCreate,
    TerritoryType,
    TerritoryUpdate,
)


class TerritoryService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TerritoryRepository(db)

    # ============================================================
    # LISTAR
    # ============================================================

    async def find_all(
        self,
        active: bool | None = None,
        territory_type: TerritoryType | None = None,
        parent_id: uuid.UUID | None = None,
    ) -> list[Territory]:

        return await self.repository.find_all(
            active=active,
            territory_type=territory_type,
            parent_id=parent_id,
        )

    # ============================================================
    # BUSCAR POR ID
    # ============================================================

    async def find_by_id(
        self,
        territory_id: uuid.UUID,
    ) -> Territory:

        territory = await self.repository.find_by_id(
            territory_id
        )

        if territory is None:
            raise LookupError(
                "El territorio no existe"
            )

        return territory

    # ============================================================
    # OBTENER HIJOS
    # ============================================================

    async def find_children(
        self,
        territory_id: uuid.UUID,
        active: bool | None = None,
    ) -> list[Territory]:

        territory = await self.repository.find_by_id(
            territory_id
        )

        if territory is None:
            raise LookupError(
                "El territorio no existe"
            )

        return await self.repository.find_children(
            parent_id=territory_id,
            active=active,
        )

    # ============================================================
    # CREAR
    # ============================================================

    async def create(
        self,
        data: TerritoryCreate,
    ) -> Territory:

        name = data.name.strip()

        code = (
            data.code.strip().upper()
            if data.code
            else None
        )

        # Validar jerarquia
        await self._validate_parent(
            territory_type=data.type,
            parent_id=data.parent_id,
        )

        # Evitar nombres duplicados dentro del mismo padre
        existing_name = (
            await self.repository.find_by_name_and_parent(
                name=name,
                parent_id=data.parent_id,
            )
        )

        if existing_name is not None:
            raise ValueError(
                "Ya existe un territorio con ese nombre dentro del mismo territorio padre"
            )

        # Validar codigo unico
        if code is not None:
            existing_code = (
                await self.repository.find_by_code(
                    code
                )
            )

            if existing_code is not None:
                raise ValueError(
                    "Ya existe un territorio con ese código"
                )

        try:
            territory = await self.repository.create(
                name=name,
                territory_type=data.type,
                parent_id=data.parent_id,
                code=code,
            )

            await self.db.commit()
            await self.db.refresh(territory)

            return territory

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # ACTUALIZAR
    # ============================================================

    async def update(
        self,
        territory_id: uuid.UUID,
        data: TerritoryUpdate,
    ) -> Territory:

        territory = await self.repository.find_by_id(
            territory_id
        )

        if territory is None:
            raise LookupError(
                "El territorio no existe"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ========================================================
        # DETERMINAR VALORES FINALES
        # ========================================================

        final_type = (
            update_data["type"]
            if "type" in update_data
            else TerritoryType(territory.type)
        )

        final_parent_id = (
            update_data["parent_id"]
            if "parent_id" in update_data
            else territory.parent_id
        )

        final_name = (
            update_data["name"].strip()
            if "name" in update_data
            else territory.name
        )

        # ========================================================
        # NO PERMITIR CAMBIAR TIPO SI TIENE HIJOS
        # ========================================================

        if (
            "type" in update_data
            and final_type.value != territory.type
        ):
            children = await self.repository.find_children(
                territory.id
            )

            if children:
                raise ValueError(
                    "No se puede cambiar el tipo de un territorio que tiene territorios hijos"
                )

        # ========================================================
        # EVITAR QUE SEA SU PROPIO PADRE
        # ========================================================

        if final_parent_id == territory.id:
            raise ValueError(
                "Un territorio no puede ser su propio padre"
            )

        # ========================================================
        # EVITAR CICLOS
        # ========================================================

        if final_parent_id is not None:
            await self._validate_no_cycle(
                territory_id=territory.id,
                new_parent_id=final_parent_id,
            )

        # ========================================================
        # VALIDAR JERARQUIA
        # ========================================================

        await self._validate_parent(
            territory_type=final_type,
            parent_id=final_parent_id,
        )

        # ========================================================
        # VALIDAR NOMBRE DUPLICADO
        # ========================================================

        existing_name = (
            await self.repository.find_by_name_and_parent(
                name=final_name,
                parent_id=final_parent_id,
            )
        )

        if (
            existing_name is not None
            and existing_name.id != territory.id
        ):
            raise ValueError(
                "Ya existe un territorio con ese nombre dentro del mismo territorio padre"
            )

        # ========================================================
        # NORMALIZAR NOMBRE
        # ========================================================

        if "name" in update_data:
            update_data["name"] = final_name

        # ========================================================
        # VALIDAR CODIGO
        # ========================================================

        if "code" in update_data:

            raw_code = update_data["code"]

            code = (
                raw_code.strip().upper()
                if raw_code
                else None
            )

            if code is not None:
                existing_code = (
                    await self.repository.find_by_code(
                        code
                    )
                )

                if (
                    existing_code is not None
                    and existing_code.id != territory.id
                ):
                    raise ValueError(
                        "Ya existe un territorio con ese código"
                    )

            update_data["code"] = code

        try:
            territory = await self.repository.update(
                territory,
                update_data,
            )

            await self.db.commit()
            await self.db.refresh(territory)

            return territory

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # DESACTIVAR
    # ============================================================

    async def deactivate(
        self,
        territory_id: uuid.UUID,
    ) -> Territory:

        territory = await self.repository.find_by_id(
            territory_id
        )

        if territory is None:
            raise LookupError(
                "El territorio no existe"
            )

        if not territory.active:
            return territory

        active_children = (
            await self.repository.find_children(
                parent_id=territory_id,
                active=True,
            )
        )

        if active_children:
            raise ValueError(
                "No se puede desactivar un territorio que tiene territorios hijos activos"
            )

        try:
            territory = await self.repository.update(
                territory,
                {
                    "active": False
                },
            )

            await self.db.commit()
            await self.db.refresh(territory)

            return territory

        except Exception:
            await self.db.rollback()
            raise

    # ============================================================
    # VALIDAR PADRE SEGUN TIPO
    # ============================================================

    async def _validate_parent(
        self,
        territory_type: TerritoryType,
        parent_id: uuid.UUID | None,
    ) -> None:

        # COUNTRY no puede tener padre
        if territory_type == TerritoryType.COUNTRY:

            if parent_id is not None:
                raise ValueError(
                    "Un país no puede tener territorio padre"
                )

            return

        # Los demás tipos necesitan padre
        if parent_id is None:
            raise ValueError(
                f"Un territorio tipo {territory_type.value} debe tener territorio padre"
            )

        parent = await self.repository.find_by_id(
            parent_id
        )

        if parent is None:
            raise ValueError(
                "El territorio padre no existe"
            )

        if not parent.active:
            raise ValueError(
                "El territorio padre está inactivo"
            )

        parent_type = TerritoryType(
            parent.type
        )

        # ========================================================
        # DEPARTMENT → COUNTRY
        # ========================================================

        if territory_type == TerritoryType.DEPARTMENT:

            if parent_type != TerritoryType.COUNTRY:
                raise ValueError(
                    "Un departamento debe pertenecer a un país"
                )

            return

        # ========================================================
        # CITY → DEPARTMENT
        # ========================================================

        if territory_type == TerritoryType.CITY:

            if parent_type != TerritoryType.DEPARTMENT:
                raise ValueError(
                    "Una ciudad debe pertenecer a un departamento"
                )

            return

        # ========================================================
        # ZONE → CITY o ZONE
        # ========================================================

        if territory_type == TerritoryType.ZONE:

            if parent_type not in (
                TerritoryType.CITY,
                TerritoryType.ZONE,
            ):
                raise ValueError(
                    "Una zona debe pertenecer a una ciudad o a otra zona"
                )

    # ============================================================
    # VALIDAR CICLOS
    # ============================================================

    async def _validate_no_cycle(
        self,
        territory_id: uuid.UUID,
        new_parent_id: uuid.UUID,
    ) -> None:

        current_parent_id: uuid.UUID | None = (
            new_parent_id
        )

        visited: set[uuid.UUID] = set()

        while current_parent_id is not None:

            if current_parent_id == territory_id:
                raise ValueError(
                    "La relación generaría un ciclo entre territorios"
                )

            # Protección adicional por si la BD ya tuviera
            # accidentalmente un ciclo.
            if current_parent_id in visited:
                raise ValueError(
                    "Se detectó una jerarquía circular en los territorios"
                )

            visited.add(
                current_parent_id
            )

            parent = await self.repository.find_by_id(
                current_parent_id
            )

            if parent is None:
                break

            current_parent_id = parent.parent_id
