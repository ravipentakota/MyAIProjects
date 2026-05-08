from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(title="Chatbot Backend")
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
