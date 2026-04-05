from fastapi import APIRouter
from app.api.routes import health, vsix, weather

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(vsix.router, prefix="/vsix", tags=["vsix"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])