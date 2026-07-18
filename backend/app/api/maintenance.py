from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.models import User
from backend.app.services.maintenance_service import maintenance_service
from backend.app.schemas.schemas import MachineResponse, MachineListResponse, MaintenanceLogResponse

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.get("/machines", response_model=MachineListResponse)
async def list_machines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    machines = await maintenance_service.get_machines(db)
    return MachineListResponse(
        total=len(machines),
        machines=[MachineResponse.model_validate(m) for m in machines],
    )


@router.get("/machines/{machine_id}", response_model=MachineResponse)
async def get_machine(
    machine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    machine = await maintenance_service.get_machine_by_id(db, machine_id)
    if not machine:
        return {"success": False, "message": "Machine not found"}
    return MachineResponse.model_validate(machine)


@router.get("/logs")
async def get_maintenance_logs(
    machine_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = await maintenance_service.get_maintenance_logs(db, machine_id, limit)
    return {
        "success": True,
        "total": len(logs),
        "logs": [MaintenanceLogResponse.model_validate(log) for log in logs],
    }


@router.get("/timeline/{machine_id}")
async def get_machine_timeline(
    machine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    timeline = await maintenance_service.get_machine_timeline(db, machine_id)
    return {"success": True, "timeline": timeline}


@router.get("/failures/{machine_id}")
async def get_failure_history(
    machine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    failures = await maintenance_service.get_failure_history(db, machine_id)
    return {
        "success": True,
        "total": len(failures),
        "failures": [MaintenanceLogResponse.model_validate(f) for f in failures],
    }
