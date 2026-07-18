from backend.app.services.rag_service import rag_service
from backend.app.core.logging_config import logger


class KnowledgeAgent:
    def query(self, question: str) -> dict:
        try:
            result = rag_service.query(question)

            risk_level = "low"
            if result["confidence"] < 30:
                risk_level = "high"
            elif result["confidence"] < 60:
                risk_level = "medium"

            return {
                "answer": result["answer"],
                "confidence": result["confidence"],
                "sources": result["sources"],
                "suggested_questions": result.get("suggested_questions", []),
                "risk_level": risk_level,
                "severity": "low",
                "recommended_action": "Verify with relevant department if confidence is below 70%.",
                "agent_type": "knowledge",
            }
        except Exception as e:
            logger.error(f"Knowledge agent error: {e}")
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "suggested_questions": [],
                "risk_level": "unknown",
                "severity": "low",
                "recommended_action": "Please try again or contact support.",
                "agent_type": "knowledge",
            }


knowledge_agent = KnowledgeAgent()
