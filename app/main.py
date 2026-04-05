from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="AI Agent API",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return { "message": "AI Agent API Running" }