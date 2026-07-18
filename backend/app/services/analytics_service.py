from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from backend.app.models.models import Document, ChatHistory, Machine, MaintenanceLog, User
from backend.app.core.logging_config import logger


class AnalyticsService:
    async def get_dashboard_stats(self, db: AsyncSession) -> dict:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_docs = await db.execute(select(func.count(Document.id)))
        docs_today = await db.execute(
            select(func.count(Document.id)).where(Document.upload_date >= today_start)
        )
        total_machines = await db.execute(select(func.count(Machine.id)))
        active_machines = await db.execute(
            select(func.count(Machine.id)).where(Machine.status == "operational")
        )
        queries_today = await db.execute(
            select(func.count(ChatHistory.id)).where(ChatHistory.timestamp >= today_start)
        )
        critical_alerts = await db.execute(
            select(func.count(MaintenanceLog.id)).where(
                MaintenanceLog.severity == "critical",
                MaintenanceLog.status != "completed",
            )
        )

        recent_uploads_result = await db.execute(
            select(Document).order_by(Document.upload_date.desc()).limit(5)
        )
        recent_chats_result = await db.execute(
            select(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(5)
        )

        machines_result = await db.execute(select(Machine))
        machines = list(machines_result.scalars().all())
        avg_health = sum(m.health_score for m in machines) / len(machines) if machines else 85.0

        failed_machines = sum(1 for m in machines if m.status == "failed")
        maintenance_machines = sum(1 for m in machines if m.status == "maintenance")
        total_m = len(machines) or 1

        compliance_score = max(0, 100 - (failed_machines * 15) - (maintenance_machines * 5))

        return {
            "total_documents": total_docs.scalar() or 0,
            "documents_today": docs_today.scalar() or 0,
            "active_machines": active_machines.scalar() or 0,
            "total_machines": total_machines.scalar() or 0,
            "ai_queries_today": queries_today.scalar() or 0,
            "critical_alerts": critical_alerts.scalar() or 0,
            "compliance_score": round(compliance_score, 1),
            "plant_health_score": round(avg_health, 1),
            "recent_uploads": list(recent_uploads_result.scalars().all()),
            "recent_conversations": list(recent_chats_result.scalars().all()),
        }

    async def get_health_score(self, db: AsyncSession) -> dict:
        machines_result = await db.execute(select(Machine))
        machines = list(machines_result.scalars().all())

        if not machines:
            return {
                "overall_score": 85.0,
                "breakdown": {
                    "machine_health": 85.0,
                    "failure_rate": 90.0,
                    "maintenance_compliance": 80.0,
                    "knowledge_coverage": 75.0,
                },
                "trend": "stable",
                "recommendations": ["Upload more equipment documentation to improve knowledge coverage"],
            }

        avg_health = sum(m.health_score for m in machines) / len(machines)
        failed = sum(1 for m in machines if m.status == "failed")
        failure_rate_score = max(0, 100 - (failed / len(machines) * 100))

        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_maintenance = await db.execute(
            select(func.count(MaintenanceLog.id)).where(MaintenanceLog.date >= thirty_days_ago)
        )
        maintenance_count = recent_maintenance.scalar() or 0
        maintenance_score = min(100, 60 + maintenance_count * 5)

        doc_count = await db.execute(select(func.count(Document.id)))
        docs = doc_count.scalar() or 0
        knowledge_score = min(100, docs * 10)

        overall = (avg_health * 0.35 + failure_rate_score * 0.25 + maintenance_score * 0.2 + knowledge_score * 0.2)

        recommendations = []
        if avg_health < 70:
            recommendations.append("Several machines have low health scores. Schedule preventive maintenance.")
        if failed > 0:
            recommendations.append(f"{failed} machine(s) in failed state. Immediate attention required.")
        if docs < 5:
            recommendations.append("Upload more documents to improve knowledge base coverage.")
        if maintenance_count == 0:
            recommendations.append("No recent maintenance recorded. Update maintenance logs.")

        trend = "improving" if overall > 75 else ("declining" if overall < 50 else "stable")

        return {
            "overall_score": round(overall, 1),
            "breakdown": {
                "machine_health": round(avg_health, 1),
                "failure_rate": round(failure_rate_score, 1),
                "maintenance_compliance": round(maintenance_score, 1),
                "knowledge_coverage": round(knowledge_score, 1),
            },
            "trend": trend,
            "recommendations": recommendations,
        }

    async def get_analytics(self, db: AsyncSession) -> dict:
        docs_by_cat = await db.execute(
            select(Document.category, func.count(Document.id))
            .group_by(Document.category)
        )
        docs_by_category = {row[0]: row[1] for row in docs_by_cat.fetchall()}

        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        upload_trends = []
        for i in range(30):
            day = thirty_days_ago + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0)
            day_end = day_start + timedelta(days=1)
            count_result = await db.execute(
                select(func.count(Document.id)).where(
                    Document.upload_date >= day_start,
                    Document.upload_date < day_end,
                )
            )
            upload_trends.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": count_result.scalar() or 0,
            })

        machines_result = await db.execute(select(Machine))
        machines = list(machines_result.scalars().all())
        machine_health = [
            {"name": m.name, "health_score": m.health_score, "status": m.status}
            for m in machines
        ]

        chat_count = await db.execute(select(func.count(ChatHistory.id)))
        ai_usage = {
            "total_queries": chat_count.scalar() or 0,
            "agent_breakdown": {},
        }
        agent_counts = await db.execute(
            select(ChatHistory.agent_type, func.count(ChatHistory.id))
            .group_by(ChatHistory.agent_type)
        )
        ai_usage["agent_breakdown"] = {row[0]: row[1] for row in agent_counts.fetchall()}

        failure_logs = await db.execute(
            select(MaintenanceLog).where(MaintenanceLog.issue_type == "corrective").order_by(MaintenanceLog.date.desc()).limit(50)
        )
        failures = list(failure_logs.scalars().all())
        failure_trends = []
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for f in failures:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
        failure_trends = [{"severity": k, "count": v} for k, v in severity_counts.items()]

        maintenance_result = await db.execute(select(func.count(MaintenanceLog.id)))
        avg_downtime_result = await db.execute(select(func.avg(MaintenanceLog.downtime_hours)))
        total_cost_result = await db.execute(select(func.sum(MaintenanceLog.cost)))

        maintenance_stats = {
            "total_records": maintenance_result.scalar() or 0,
            "avg_downtime_hours": round(avg_downtime_result.scalar() or 0, 1),
            "total_cost": round(total_cost_result.scalar() or 0, 2),
        }

        return {
            "documents_by_category": docs_by_category,
            "upload_trends": upload_trends,
            "machine_health": machine_health,
            "ai_usage": ai_usage,
            "failure_trends": failure_trends,
            "top_searched_equipment": [
                {"name": m.name, "queries": 0} for m in machines[:5]
            ],
            "maintenance_stats": maintenance_stats,
        }


analytics_service = AnalyticsService()
