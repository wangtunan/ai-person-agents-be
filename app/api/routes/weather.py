from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.weather import get_weather_agent, get_weather_agent_stream

router = APIRouter()

@router.get("")
def weather(city: str):
    return get_weather_agent(city)

@router.get("/stream")
def weather_stream(city: str):
    return StreamingResponse(
        get_weather_agent_stream(city),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )