from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/bot",
    tags=["bot"],
)


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "scope": "bot",
    }
