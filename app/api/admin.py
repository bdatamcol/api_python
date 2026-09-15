from fastapi import APIRouter

from app.modules.brands.router import router as brands_router
from app.modules.categories.router import router as categories_router
from app.modules.colors.router import router as colors_router
from app.modules.territories.router import router as territories_router
from app.modules.stores.router import router as stores_router
from app.modules.price_lists.router import router as price_lists_router
from app.modules.motorcycles.router import router as motorcycles_router
from app.modules.motorcycle_aliases.router import (
    router as motorcycle_aliases_router,
)


router = APIRouter(
    prefix="/api/v1/admin",
)


router.include_router(brands_router)
router.include_router(categories_router)
router.include_router(colors_router)
router.include_router(territories_router)
router.include_router(stores_router)
router.include_router(price_lists_router)
router.include_router(motorcycles_router)
router.include_router(motorcycle_aliases_router)


@router.get(
    "/health",
    tags=["Admin"],
)
async def health():
    return {
        "status": "ok",
        "service": "admin",
    }
