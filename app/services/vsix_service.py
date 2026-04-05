import requests
import os
from urllib.parse import urlparse

DOWNLOAD_DIR = "downloads"

def _extra_filename(url: str) -> str:
    path = urlparse(url).path
    filename = os.path.basename(path)

    if not filename:
        filename = "plugin.vsix"
    
    return filename

def download_vsix(url: str):
    response = requests.get(url)
    response.raise_for_status()

    filename = _extra_filename(url)

    return {
        "content": response.content,
        "filename": filename,
        "content_type": response.headers.get(
            "Content-Type",
            "application/octet-stream"
        )
    }