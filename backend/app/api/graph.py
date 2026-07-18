from fastapi import APIRouter, Depends, Query
from typing import Optional
from backend.app.core.security import get_current_user
from backend.app.models.models import User
from backend.app.services.graph_service import graph_service
from backend.app.schemas.schemas import GraphResponse

router = APIRouter(prefix="/api/graph", tags=["Knowledge Graph"])


@router.get("", response_model=GraphResponse)
async def get_graph(
    current_user: User = Depends(get_current_user),
):
    data = graph_service.get_full_graph()
    return GraphResponse(**data)


@router.get("/machine/{machine_name}")
async def get_machine_graph(
    machine_name: str,
    current_user: User = Depends(get_current_user),
):
    data = graph_service.get_machine_subgraph(machine_name)
    return {"success": True, **data}
