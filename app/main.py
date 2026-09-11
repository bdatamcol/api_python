from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.bot import router as bot_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env,
    }


app.include_router(admin_router)
app.include_router(bot_router)
