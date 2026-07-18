from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend.app.models.models import Machine, MaintenanceLog
from backend.app.services.rag_service import rag_service
from backend.app.services.groq_service import groq_service
from backend.app.core.logging_config import logger


class MaintenanceService:
    async def get_machines(self, db: AsyncSession) -> List[Machine]:
        result = await db.execute(select(Machine).order_by(Machine.name))
        return list(result.scalars().all())

    async def get_machine_by_id(self, db: AsyncSession, machine_id: int) -> Optional[Machine]:
        result = await db.execute(select(Machine).where(Machine.id == machine_id))
        return result.scalar_one_or_none()

    async def get_machine_by_name(self, db: AsyncSession, name: str) -> Optional[Machine]:
        result = await db.execute(select(Machine).where(Machine.name.ilike(f"%{name}%")))
        return result.scalar_one_or_none()

    async def get_maintenance_logs(
        self,
        db: AsyncSession,
        machine_id: Optional[int] = None,
        limit: int = 50,
    ) -> List[MaintenanceLog]:
        query = select(MaintenanceLog).order_by(desc(MaintenanceLog.date))
        if machine_id:
            query = query.where(MaintenanceLog.machine_id == machine_id)
        query = query.limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_failure_history(self, db: AsyncSession, machine_id: int) -> List[MaintenanceLog]:
        result = await db.execute(
            select(MaintenanceLog)
            .where(MaintenanceLog.machine_id == machine_id)
            .where(MaintenanceLog.issue_type == "corrective")
            .order_by(desc(MaintenanceLog.date))
        )
        return list(result.scalars().all())

    async def query_maintenance(
        self,
        db: AsyncSession,
        question: str,
        machine_id: Optional[int] = None,
    ) -> dict:
        context_parts = []

        if machine_id:
            machine = await self.get_machine_by_id(db, machine_id)
            if machine:
                context_parts.append(
                    f"Machine: {machine.name}, Type: {machine.machine_type}, "
                    f"Status: {machine.status}, Health: {machine.health_score}%"
                )
                logs = await self.get_maintenance_logs(db, machine_id, limit=10)
                for log in logs:
                    context_parts.append(
                        f"[{log.date.strftime('%Y-%m-%d')}] Issue: {log.issue}, "
                        f"Action: {log.action_taken}, Severity: {log.severity}, "
                        f"Engineer: {log.engineer}"
                    )

        rag_result = rag_service.query(question, filter_metadata=None)

        maintenance_context = "\n".join(context_parts)
        if maintenance_context:
            full_context = f"Maintenance Database Records:\n{maintenance_context}\n\nDocument Context:\n{rag_result.get('context_used', '')}"
        else:
            full_context = rag_result.get("context_used", "")

        system_prompt = """You are a Maintenance Intelligence Agent for an industrial plant. You analyze maintenance records, failure patterns, and equipment history to provide actionable maintenance recommendations.

For every response, provide:
1. Analysis of the issue based on available data
2. Historical precedents if any exist
3. Recommended maintenance actions
4. Spare parts that may be needed
5. Estimated priority/severity
6. Preventive measures to avoid recurrence

Always cite source documents and maintenance records."""

        answer = groq_service.generate_with_context(
            system_prompt=system_prompt,
            context=full_context,
            question=question,
        )

        return {
            "answer": answer,
            "confidence": rag_result.get("confidence", 0.0),
            "sources": rag_result.get("sources", []),
            "maintenance_records_used": len(context_parts),
        }

    async def get_machine_timeline(self, db: AsyncSession, machine_id: int) -> List[dict]:
        logs = await self.get_maintenance_logs(db, machine_id, limit=20)
        timeline = []
        for log in logs:
            timeline.append({
                "date": log.date.isoformat(),
                "type": log.issue_type,
                "title": log.issue[:100],
                "description": log.action_taken,
                "severity": log.severity,
                "engineer": log.engineer,
                "status": log.status,
            })
        return timeline


maintenance_service = MaintenanceService()
