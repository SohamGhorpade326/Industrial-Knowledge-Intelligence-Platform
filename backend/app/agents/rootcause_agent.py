from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.models.models import MaintenanceLog, Machine
from backend.app.services.rag_service import rag_service
from backend.app.services.groq_service import groq_service
from backend.app.core.logging_config import logger

ROOTCAUSE_PROMPT = """You are a Root Cause Analysis (RCA) Agent for an industrial manufacturing plant. You analyze equipment failures to determine probable root causes.

Your analysis should include:
1. **Probable Root Causes** - Listed by likelihood (with confidence percentage)
2. **Evidence** - What data supports each hypothesis
3. **Contributing Factors** - Environmental, operational, or maintenance factors
4. **Similar Historical Incidents** - Past failures with similar patterns
5. **Corrective Actions** - Immediate fixes and long-term solutions
6. **Preventive Measures** - How to prevent recurrence

Use the 5-Why methodology or Fishbone (Ishikawa) analysis structure when appropriate.
Always cite maintenance records and documents used in the analysis."""


class RootCauseAgent:
    async def analyze(
        self,
        db: AsyncSession,
        question: str,
        machine_id: Optional[int] = None,
    ) -> dict:
        try:
            context_parts = []

            if machine_id:
                machine_result = await db.execute(
                    select(Machine).where(Machine.id == machine_id)
                )
                machine = machine_result.scalar_one_or_none()
                if machine:
                    context_parts.append(
                        f"Machine: {machine.name}, Type: {machine.machine_type}, "
                        f"Manufacturer: {machine.manufacturer}, Status: {machine.status}, "
                        f"Health Score: {machine.health_score}%, Operating Hours: {machine.operating_hours}"
                    )

                logs_result = await db.execute(
                    select(MaintenanceLog)
                    .where(MaintenanceLog.machine_id == machine_id)
                    .order_by(desc(MaintenanceLog.date))
                    .limit(15)
                )
                logs = list(logs_result.scalars().all())
                for log in logs:
                    context_parts.append(
                        f"[{log.date.strftime('%Y-%m-%d')}] Issue: {log.issue} | "
                        f"Type: {log.issue_type} | Severity: {log.severity} | "
                        f"Action: {log.action_taken} | Engineer: {log.engineer} | "
                        f"Downtime: {log.downtime_hours}h | Parts: {', '.join(log.spare_parts_used or [])}"
                    )

            rag_result = rag_service.query(question)

            maintenance_context = "\n".join(context_parts)
            full_context = f"Maintenance Records:\n{maintenance_context}\n\nDocument Knowledge:\n{rag_result.get('context_used', '')}"

            answer = groq_service.generate_with_context(
                system_prompt=ROOTCAUSE_PROMPT,
                context=full_context,
                question=question,
            )

            confidence = rag_result.get("confidence", 0.0)
            if context_parts:
                confidence = min(confidence + 15, 95.0)

            return {
                "answer": answer,
                "confidence": confidence,
                "sources": rag_result.get("sources", []),
                "maintenance_records_analyzed": len(context_parts),
                "suggested_questions": [
                    "What preventive maintenance can avoid this in the future?",
                    "Are there similar failures in other machines?",
                    "What is the estimated cost of this repair?",
                ],
                "risk_level": "high",
                "severity": "high",
                "recommended_action": "Conduct detailed root cause investigation with maintenance team.",
                "agent_type": "rootcause",
            }
        except Exception as e:
            logger.error(f"Root cause agent error: {e}")
            return {
                "answer": f"Error during root cause analysis: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "maintenance_records_analyzed": 0,
                "suggested_questions": [],
                "risk_level": "unknown",
                "severity": "unknown",
                "recommended_action": "Contact engineering team for manual analysis.",
                "agent_type": "rootcause",
            }


rootcause_agent = RootCauseAgent()
