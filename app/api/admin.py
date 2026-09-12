from fastapi import APIRouter

from app.modules.brands.router import router as brands_router
from app.modules.categories.router import router as categories_router
from app.modules.colors.router import router as colors_router


router = APIRouter(
    prefix="/api/v1/admin",
)


router.include_router(
    brands_router
)

router.include_router(
    categories_router
)

router.include_router(
    colors_router
)


@router.get(
    "/health",
    tags=["Admin"],
)
async def health():
    return {
        "status": "ok",
        "service": "admin",
    }
