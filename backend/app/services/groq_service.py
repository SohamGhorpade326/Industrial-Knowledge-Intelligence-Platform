from typing import Optional, List
from backend.app.core.config import get_settings
from backend.app.core.logging_config import logger

settings = get_settings()


class GroqService:
    def __init__(self):
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set. AI features will be disabled.")
            return
        try:
            from groq import Groq
            self._client = Groq(api_key=settings.GROQ_API_KEY)
            self._available = True
            logger.info(f"Groq client initialized with model: {settings.GROQ_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")

    @property
    def is_available(self) -> bool:
        return self._available

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        if not self._available:
            return "AI service is currently unavailable. Please configure the GROQ_API_KEY in your .env file."

        try:
            response = self._client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return f"AI service error: {str(e)}"

    def generate_with_context(
        self,
        system_prompt: str,
        context: str,
        question: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        user_message = f"""Context from industrial documents:
---
{context}
---

Question: {question}

Provide a detailed, accurate answer based strictly on the context above. Include specific references to source documents and page numbers when available. If the context doesn't contain enough information to answer fully, state what is known and what additional information would be needed."""

        return self.generate_response(system_prompt, user_message, temperature, max_tokens)

    def generate_structured_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        return self.generate_response(system_prompt, user_message, temperature, max_tokens)


groq_service = GroqService()
