from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.vsix import vsix_stream_agent

router = APIRouter()

@router.post("/stream")
def get_vsix_stream(payload: dict):
    url = payload.get("url")
    print("get_vsix_stream", url)
    return StreamingResponse(
        vsix_stream_agent(url),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )