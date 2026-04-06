from fastapi import APIRouter
from fastapi.responses import Response
from app.services.vsix_service import download_vsix

router = APIRouter()

@router.post("")
def download(payload: dict):
    url = payload.get("url")
    
    if not url:
        return { "error": "url is required" }
    
    result = download_vsix(url)

    return Response(
        content=result["content"],
        media_type=result["content_type"],
        headers={
            "Content-Disposition": f"attachment; filename={result['filename']}"
        }
    )
