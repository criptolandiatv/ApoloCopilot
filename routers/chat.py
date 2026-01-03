"""AI Chatbot routes"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import get_db
from models.user import User
from models.chat import ChatMessage
from utils.security import get_verified_user
from services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api/chat", tags=["Chat"])
chatbot_service = ChatbotService()


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    message: str
    response: str | None
    created_at: str

    class Config:
        from_attributes = True


@router.post("/send")
async def send_message(
    data: ChatMessageRequest,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    """Send a message to the AI chatbot"""
    try:
        chat_message = await chatbot_service.get_ai_response(
            user_id=current_user.id, message=data.message, db=db
        )

        return {
            "id": chat_message.id,
            "message": chat_message.message,
            "response": chat_message.response,
            "source": chat_message.source,
            "created_at": chat_message.created_at.isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")


@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    limit: int = 20, current_user: User = Depends(get_verified_user), db: Session = Depends(get_db)
):
    """Get chat history"""
    messages = await chatbot_service.get_chat_history(user_id=current_user.id, db=db, limit=limit)

    return messages


@router.get("/info")
async def get_chatbot_info():
    """Get chatbot information"""
    return {
        "name": "ApoloCopilot Assistant",
        "description": "Assistente inteligente integrado com OpenEvidence",
        "capabilities": [
            "Respostas baseadas em evidências científicas",
            "Informações sobre o sistema",
            "Ajuda com funcionalidades",
            "Conversação natural",
        ],
        "data_source": "OpenEvidence.com",
        "language": "Português",
    }


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            user_id = data.get("user_id")  # In production, verify from token

            if not user_id:
                await websocket.send_json({"error": "user_id required"})
                continue

            # Get AI response
            chat_message = await chatbot_service.get_ai_response(
                user_id=user_id, message=message, db=db
            )

            # Send response
            await websocket.send_json(
                {
                    "id": chat_message.id,
                    "message": chat_message.message,
                    "response": chat_message.response,
                    "created_at": chat_message.created_at.isoformat(),
                }
            )

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
