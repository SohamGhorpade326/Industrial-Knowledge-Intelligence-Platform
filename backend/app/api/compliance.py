from fastapi import APIRouter, Depends
from backend.app.core.security import get_current_user
from backend.app.models.models import User
from backend.app.services.compliance_service import compliance_service
from backend.app.schemas.schemas import ComplianceQueryRequest

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


@router.post("/query")
async def query_compliance(
    request: ComplianceQueryRequest,
    current_user: User = Depends(get_current_user),
):
    result = compliance_service.query_compliance(request.question)
    return {"success": True, **result}


@router.post("/checklist")
async def generate_checklist(
    request: ComplianceQueryRequest,
    current_user: User = Depends(get_current_user),
):
    result = compliance_service.generate_checklist(request.question)
    return {"success": True, **result}
