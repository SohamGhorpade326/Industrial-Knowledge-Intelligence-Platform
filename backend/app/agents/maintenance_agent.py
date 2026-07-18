from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.maintenance_service import maintenance_service
from backend.app.services.groq_service import groq_service
from backend.app.core.logging_config import logger

MAINTENANCE_PROMPT = """You are a Maintenance Intelligence Agent for an industrial manufacturing plant. You specialize in:
1. Diagnosing equipment failures and identifying root causes
2. Recommending maintenance actions based on historical data
3. Suggesting spare parts and replacement schedules
4. Predicting potential failures based on patterns
5. Providing step-by-step repair procedures

Always provide:
- Specific, actionable recommendations
- Historical precedent when available
- Severity assessment
- Estimated repair time
- Required spare parts
- Safety precautions during maintenance

Cite all sources and maintenance records used in your analysis."""


class MaintenanceAgent:
    async def query(
        self,
        db: AsyncSession,
        question: str,
        machine_id: Optional[int] = None,
    ) -> dict:
        try:
            result = await maintenance_service.query_maintenance(db, question, machine_id)

            severity = "medium"
            critical_keywords = ["failure", "broken", "emergency", "critical", "urgent"]
            if any(kw in question.lower() for kw in critical_keywords):
                severity = "high"

            recommended_action = "Schedule preventive maintenance inspection."
            if severity == "high":
                recommended_action = "Immediate attention required. Dispatch maintenance team."

            return {
                "answer": result["answer"],
                "confidence": result["confidence"],
                "sources": result["sources"],
                "suggested_questions": [
                    "What spare parts are needed for this repair?",
                    "How long is the estimated downtime?",
                    "Are there similar historical failures?",
                ],
                "risk_level": severity,
                "severity": severity,
                "recommended_action": recommended_action,
                "agent_type": "maintenance",
            }
        except Exception as e:
            logger.error(f"Maintenance agent error: {e}")
            return {
                "answer": f"Error processing maintenance query: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "suggested_questions": [],
                "risk_level": "unknown",
                "severity": "unknown",
                "recommended_action": "Contact maintenance supervisor.",
                "agent_type": "maintenance",
            }


maintenance_agent = MaintenanceAgent()
