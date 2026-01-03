"""AI Chatbot service integrated with OpenEvidence"""

import os
import httpx
from typing import Optional
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from models.chat import ChatMessage

load_dotenv()

OPENEVIDENCE_API_KEY = os.getenv("OPENEVIDENCE_API_KEY")
OPENEVIDENCE_BASE_URL = os.getenv("OPENEVIDENCE_BASE_URL", "https://openevidence.com/api")


class ChatbotService:
    def __init__(self):
        self.api_key = OPENEVIDENCE_API_KEY
        self.base_url = OPENEVIDENCE_BASE_URL

    async def get_ai_response(self, user_id: int, message: str, db: Session) -> ChatMessage:
        """Get AI response from OpenEvidence API"""
        # Save user message
        chat_message = ChatMessage(user_id=user_id, message=message, is_ai_response=False)
        db.add(chat_message)
        db.commit()

        # Get AI response
        response_text = await self._query_openevidence(message)

        # Save AI response
        chat_message.response = response_text
        db.commit()
        db.refresh(chat_message)

        return chat_message

    async def _query_openevidence(self, query: str) -> str:
        """Query OpenEvidence API"""
        if not self.api_key:
            # Fallback response if API not configured
            return self._generate_fallback_response(query)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/query",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"query": query, "max_results": 3},
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._format_response(data)
                else:
                    return self._generate_fallback_response(query)

        except Exception as e:
            print(f"OpenEvidence API error: {e}")
            return self._generate_fallback_response(query)

    def _format_response(self, data: dict) -> str:
        """Format OpenEvidence API response"""
        if not data or "results" not in data:
            return "Desculpe, não encontrei informações relevantes para sua pergunta."

        results = data["results"]
        if not results:
            return "Desculpe, não encontrei informações relevantes para sua pergunta."

        # Format results
        response_parts = []
        for i, result in enumerate(results[:3], 1):
            title = result.get("title", "")
            summary = result.get("summary", "")
            source = result.get("source", "")

            response_parts.append(f"**{i}. {title}**\n{summary}")
            if source:
                response_parts.append(f"Fonte: {source}")

        return "\n\n".join(response_parts)

    def _generate_fallback_response(self, query: str) -> str:
        """Generate fallback response when API is not available"""
        query_lower = query.lower()

        # Simple keyword-based responses
        if any(word in query_lower for word in ["olá", "oi", "hello", "hi"]):
            return "Olá! Sou o assistente ApoloCopilot. Como posso ajudá-lo hoje?"

        elif any(word in query_lower for word in ["ajuda", "help", "como"]):
            return (
                "Posso ajudá-lo com:\n"
                "• Informações baseadas em evidências científicas\n"
                "• Gerenciamento de calendário\n"
                "• Localização e navegação\n"
                "• Participação no fórum\n\n"
                "O que você gostaria de saber?"
            )

        elif any(word in query_lower for word in ["obrigado", "thanks", "valeu"]):
            return "De nada! Estou aqui para ajudar. 😊"

        else:
            return (
                f"Você perguntou: '{query}'\n\n"
                "No momento, estou processando sua pergunta. "
                "Para respostas baseadas em evidências científicas, "
                "certifique-se de que a integração com OpenEvidence está configurada."
            )

    async def get_chat_history(
        self, user_id: int, db: Session, limit: int = 20
    ) -> list[ChatMessage]:
        """Get user's chat history"""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
