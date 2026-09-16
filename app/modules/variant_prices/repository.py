import uuid
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.variant_prices.model import VariantPrice


class VariantPriceRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # BUSCAR PRECIO POR ID
    # ============================================================

    async def find_by_id(
        self,
        price_id: uuid.UUID,
    ) -> VariantPrice | None:

        query = select(VariantPrice).where(
            VariantPrice.id == price_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # ============================================================
    # HISTORIAL DE PRECIOS DE UNA VARIANTE
    #
    # Puede filtrarse opcionalmente por lista de precios.
    # ============================================================

    async def find_all_by_variant(
        self,
        variant_id: uuid.UUID,
        price_list_id: uuid.UUID | None = None,
        active: bool | None = None,
    ) -> list[VariantPrice]:

        query = select(VariantPrice).where(
            VariantPrice.variant_id == variant_id
        )

        if price_list_id is not None:
            query = query.where(
                VariantPrice.price_list_id
                == price_list_id
            )

        if active is not None:
            query = query.where(
                VariantPrice.active == active
            )

        query = query.order_by(
            VariantPrice.valid_from.desc(),
            VariantPrice.created_at.desc(),
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # OBTENER PRECIO VIGENTE
    #
    # Busca el precio que esté activo para una fecha determinada.
    #
    # Si no enviamos fecha, el service podrá mandar date.today().
    # ============================================================

    async def find_current(
        self,
        variant_id: uuid.UUID,
        price_list_id: uuid.UUID,
        on_date: date,
    ) -> VariantPrice | None:

        query = (
            select(VariantPrice)
            .where(
                VariantPrice.variant_id
                == variant_id,

                VariantPrice.price_list_id
                == price_list_id,

                VariantPrice.active.is_(True),

                VariantPrice.valid_from
                <= on_date,

                or_(
                    VariantPrice.valid_until.is_(None),
                    VariantPrice.valid_until
                    >= on_date,
                ),
            )
            .order_by(
                VariantPrice.valid_from.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().first()

    # ============================================================
    # BUSCAR PERIODOS QUE SE CRUCEN
    #
    # Sirve para evitar:
    #
    # Precio A:
    # 01/09/2026 -> 30/09/2026
    #
    # Precio B:
    # 15/09/2026 -> NULL
    #
    # porque ambos se cruzan.
    #
    # exclude_price_id se usará al editar un precio para que
    # no se detecte a sí mismo.
    # ============================================================

    async def find_overlapping(
        self,
        variant_id: uuid.UUID,
        price_list_id: uuid.UUID,
        valid_from: date,
        valid_until: date | None,
        exclude_price_id: uuid.UUID | None = None,
    ) -> list[VariantPrice]:

        query = select(VariantPrice).where(
            VariantPrice.variant_id
            == variant_id,

            VariantPrice.price_list_id
            == price_list_id,

            VariantPrice.active.is_(True),

            # El precio existente debe terminar después
            # de que comience el nuevo.
            or_(
                VariantPrice.valid_until.is_(None),
                VariantPrice.valid_until
                >= valid_from,
            ),
        )

        # Si el nuevo precio tiene fecha final,
        # el existente debe comenzar antes de que termine.
        if valid_until is not None:
            query = query.where(
                VariantPrice.valid_from
                <= valid_until
            )

        if exclude_price_id is not None:
            query = query.where(
                VariantPrice.id
                != exclude_price_id
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    # ============================================================
    # CREAR PRECIO
    # ============================================================

    async def create(
        self,
        variant_id: uuid.UUID,
        price_list_id: uuid.UUID,
        amount: int,
        valid_from: date,
        valid_until: date | None,
        source_reference: str | None,
    ) -> VariantPrice:

        price = VariantPrice(
            variant_id=variant_id,
            price_list_id=price_list_id,
            amount=amount,
            valid_from=valid_from,
            valid_until=valid_until,
            source_reference=source_reference,
        )

        self.db.add(price)

        await self.db.flush()
        await self.db.refresh(price)

        return price

    # ============================================================
    # ACTUALIZAR PRECIO
    # ============================================================

    async def update(
        self,
        price: VariantPrice,
        data: dict,
    ) -> VariantPrice:

        for field, value in data.items():
            setattr(
                price,
                field,
                value,
            )

        await self.db.flush()
        await self.db.refresh(price)

        return price
