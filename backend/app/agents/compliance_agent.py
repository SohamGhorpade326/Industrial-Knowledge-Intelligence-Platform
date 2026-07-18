from backend.app.services.compliance_service import compliance_service
from backend.app.core.logging_config import logger


class ComplianceAgent:
    def query(self, question: str) -> dict:
        try:
            result = compliance_service.query_compliance(question)

            safety_keywords = ["safety", "hazard", "ppe", "emergency", "danger", "toxic", "fire"]
            is_safety_critical = any(kw in question.lower() for kw in safety_keywords)

            severity = "high" if is_safety_critical else "medium"
            risk_level = "high" if is_safety_critical else "low"

            recommended_action = "Review and verify compliance status with safety officer."
            if is_safety_critical:
                recommended_action = "CRITICAL: Verify safety procedures immediately. Do not proceed without proper PPE and authorization."

            return {
                "answer": result["answer"],
                "confidence": result["confidence"],
                "sources": result["sources"],
                "suggested_questions": result.get("suggested_questions", [
                    "What PPE is required for this procedure?",
                    "What are the regulatory requirements?",
                    "Is there a compliance checklist available?",
                ]),
                "risk_level": risk_level,
                "severity": severity,
                "recommended_action": recommended_action,
                "agent_type": "compliance",
            }
        except Exception as e:
            logger.error(f"Compliance agent error: {e}")
            return {
                "answer": f"Error processing compliance query: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "suggested_questions": [],
                "risk_level": "unknown",
                "severity": "unknown",
                "recommended_action": "Contact safety officer immediately.",
                "agent_type": "compliance",
            }


compliance_agent = ComplianceAgent()
