from fastapi import FastAPI

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.appointments import router as appointments_router
from app.api.v1.routers.doctors import router as doctors_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(doctors_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}