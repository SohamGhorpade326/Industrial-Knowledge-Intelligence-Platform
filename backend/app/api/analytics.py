from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.models import User
from backend.app.services.analytics_service import analytics_service
from backend.app.schemas.schemas import AnalyticsResponse

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await analytics_service.get_analytics(db)
    return AnalyticsResponse(**data)
