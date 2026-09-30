import uuid
from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.variant_prices.schemas import (
    VariantPriceCreateForVariant,
    VariantPriceResponse,
    VariantPriceUpdate,
)
from app.modules.variant_prices.service import (
    VariantPriceService,
)


router = APIRouter(
    tags=["Admin - Variant Prices"],
)


# ============================================================
# LISTAR HISTORIAL DE PRECIOS DE UNA VARIANTE
# ============================================================

@router.get(
    "/motorcycle-variants/{variant_id}/prices",
    response_model=list[VariantPriceResponse],
    status_code=status.HTTP_200_OK,
)
async def list_variant_prices(
    variant_id: uuid.UUID,
    price_list_id: uuid.UUID | None = Query(
        default=None,
        description="Filtrar por lista de precios",
    ),
    active: bool | None = Query(
        default=None,
        description="Filtrar precios activos o inactivos",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = VariantPriceService(db)

    try:
        return await service.find_all_by_variant(
            variant_id=variant_id,
            price_list_id=price_list_id,
            active=active,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# OBTENER PRECIO VIGENTE
#
# Ejemplo:
#
# GET
# /motorcycle-variants/{variant_id}/prices/current
# ?price_list_id=...
#
# También permite consultar una fecha histórica:
#
# ?price_list_id=...&on_date=2026-09-01
# ============================================================

@router.get(
    "/motorcycle-variants/{variant_id}/prices/current",
    response_model=VariantPriceResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_variant_price(
    variant_id: uuid.UUID,
    price_list_id: uuid.UUID = Query(
        ...,
        description="Lista de precios que se desea consultar",
    ),
    on_date: date | None = Query(
        default=None,
        description="Fecha a consultar. Si se omite se usa la fecha actual.",
    ),
    db: AsyncSession = Depends(get_db),
):
    service = VariantPriceService(db)

    try:
        return await service.find_current(
            variant_id=variant_id,
            price_list_id=price_list_id,
            on_date=on_date,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# CREAR PRECIO PARA UNA VARIANTE
# ============================================================

@router.post(
    "/motorcycle-variants/{variant_id}/prices",
    response_model=VariantPriceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_variant_price(
    variant_id: uuid.UUID,
    data: VariantPriceCreateForVariant,
    db: AsyncSession = Depends(get_db),
):
    service = VariantPriceService(db)

    try:
        return await service.create_for_variant(
            variant_id=variant_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# OBTENER PRECIO POR ID
# ============================================================

@router.get(
    "/variant-prices/{price_id}",
    response_model=VariantPriceResponse,
    status_code=status.HTTP_200_OK,
)
async def get_variant_price(
    price_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = VariantPriceService(db)

    try:
        return await service.find_by_id(
            price_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


# ============================================================
# ACTUALIZAR PRECIO
# ============================================================

@router.patch(
    "/variant-prices/{price_id}",
    response_model=VariantPriceResponse,
    status_code=status.HTTP_200_OK,
)
async def update_variant_price(
    price_id: uuid.UUID,
    data: VariantPriceUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = VariantPriceService(db)

    try:
        return await service.update(
            price_id=price_id,
            data=data,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# DESACTIVAR PRECIO
# ============================================================

@router.delete(
    "/variant-prices/{price_id}",
    response_model=VariantPriceResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_variant_price(
    price_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = VariantPriceService(db)

    try:
        return await service.deactivate(
            price_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
