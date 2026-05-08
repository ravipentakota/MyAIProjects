from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    response = await chat_service.send_message(payload.message)
    return ChatResponse(reply=response)
