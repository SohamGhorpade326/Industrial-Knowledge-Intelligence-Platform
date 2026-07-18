from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.models import User
from backend.app.services.analytics_service import analytics_service
from backend.app.schemas.schemas import DashboardStats, HealthScoreResponse, DocumentResponse, ChatHistoryResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = await analytics_service.get_dashboard_stats(db)
    return {
        "success": True,
        "total_documents": stats["total_documents"],
        "documents_today": stats["documents_today"],
        "active_machines": stats["active_machines"],
        "total_machines": stats["total_machines"],
        "ai_queries_today": stats["ai_queries_today"],
        "critical_alerts": stats["critical_alerts"],
        "compliance_score": stats["compliance_score"],
        "plant_health_score": stats["plant_health_score"],
        "recent_uploads": [
            DocumentResponse.model_validate(d) for d in stats["recent_uploads"]
        ],
        "recent_conversations": [
            ChatHistoryResponse.model_validate(c) for c in stats["recent_conversations"]
        ],
    }


@router.get("/health-score", response_model=HealthScoreResponse)
async def get_health_score(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await analytics_service.get_health_score(db)
    return HealthScoreResponse(**data)
