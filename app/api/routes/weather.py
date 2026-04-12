from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.weather import get_weather_agent_stream

router = APIRouter()

@router.get("/stream")
def weather_stream(text: str):
    return StreamingResponse(
        get_weather_agent_stream(text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )