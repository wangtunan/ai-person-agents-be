import os
import json
import re
import requests
from urllib.parse import unquote
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv();

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MARKETPLACE_API = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"

def parse_url(url: str):
    if "marketplace.visualstudio.com" not in url:
        raise ValueError("Invalid marketplace domain")

    match = re.search(r"itemName=([^.]+)\.([^.]+)", url)
    print("match", match)
    if not match:
        raise ValueError("Invalid VSCode marketplace URL")

    return match.group(1), match.group(2)

def fetch_extension(publisher: str, extension: str):
    payload = {
        "filters": [
            {
                "criteria": [
                    {"filterType": 7, "value": f"{publisher}.{extension}"}
                ]
            }
        ],
        "flags": 103
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;api-version=3.0-preview.1"
    }

    res = requests.post(MARKETPLACE_API, json=payload, headers=headers)
    res.raise_for_status()

    data = res.json()
    exts = data.get("results", [])[0].get("extensions", [])

    if not exts:
        raise ValueError("Extension not found")

    return exts[0]

def build_vsix_download_url(publisher: str, extension: str, version: str):
    return f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension}/{version}/vspackage"


def build_clean_data(publisher: str, extension: str, ext: dict):
    versions = ext.get("versions", [])

    return {
        "name": ext.get("name", ""),
        "publisher": ext.get("publisher", ""),
        "extension": extension,
        "description": ext.get("description", ""),
        "versions": [
            {
                "version": v["version"],
                "download_url": build_vsix_download_url(publisher, extension, v["version"])
            }
            for v in versions[:3]
        ]
    }

def generate_result(clean_data: dict):
    system_prompt = f"""
        You are a helpful assistant that generates clean Markdown for a VSCode extension.
        Response in Markdown format, Example:
        * Version1: download link
        * Version2: download link
        * Version3: download link

        Always Respond In Chinese. 
    """
    user_prompt = f"""
        Generate clean Markdown for a VSCode extension.

        Requirements:
        - Use Markdown format
        - Include name, publisher, description
        - List latest versions
        - Each version must include a clickable VSIX download link
        - No extra explanation

        Data:
        {json.dumps(clean_data, ensure_ascii=False)}
    """

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        stream=True,
    )
    return response


def vsix_stream_agent(url: str):
    """SSE: delta events (Markdown text), then done — same JSON shape as weather stream."""
    url = unquote(url)
    publisher, extension = parse_url(url)
    result = fetch_extension(publisher, extension)
    clean_data = build_clean_data(publisher, extension, result)
    return_result = generate_result(clean_data)
    for chunk in return_result:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield f"data: {json.dumps({'type': 'delta', 'text': delta.content}, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

if __name__ == "__main__":
    url = "https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance"
    for raw in vsix_stream_agent(url):
        line = raw.strip()
        if not line.startswith("data:"):
            continue
        payload = json.loads(line.removeprefix("data:").strip())
        if payload.get("type") == "delta":
            print(payload.get("text", ""), end="", flush=True)
        elif payload.get("type") == "done":
            print()
    