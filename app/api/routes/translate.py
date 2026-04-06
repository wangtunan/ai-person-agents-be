from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.translate import translate_agent_stream

router = APIRouter()


class TranslateStreamBody(BaseModel):
    text: str = Field(..., min_length=1)


@router.post("/stream")
def get_translate_stream(body: TranslateStreamBody):
    return StreamingResponse(
        translate_agent_stream(body.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )