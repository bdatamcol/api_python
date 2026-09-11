from fastapi import APIRouter

from app.modules.brands.router import router as brands_router


router = APIRouter(
    prefix="/api/v1/admin",
)


# ============================================================
# ROUTERS ADMINISTRATIVOS
# ============================================================

router.include_router(
    brands_router
)


# ============================================================
# HEALTH
# ============================================================

@router.get(
    "/health",
    tags=["Admin"],
)
async def health():
    return {
        "status": "ok",
        "service": "admin",
    }
