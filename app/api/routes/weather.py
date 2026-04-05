from fastapi import APIRouter
from app.services.weather_service import get_weather

router = APIRouter()

@router.get("/")
def weather(city: str):
    return get_weather(city)