from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.models import User, ChatHistory
from backend.app.schemas.schemas import (
    ChatRequest, ChatResponse, ChatHistoryResponse,
    MaintenanceQueryRequest, ComplianceQueryRequest,
    EmergencyQueryRequest, EmergencyResponse, CitationSource,
)
from backend.app.agents.knowledge_agent import knowledge_agent
from backend.app.agents.maintenance_agent import maintenance_agent
from backend.app.agents.compliance_agent import compliance_agent
from backend.app.agents.emergency_agent import emergency_agent
from backend.app.agents.rootcause_agent import rootcause_agent
from backend.app.utils.helpers import generate_session_id
from backend.app.core.logging_config import logger

router = APIRouter(prefix="/api", tags=["AI Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_id = request.session_id or generate_session_id()

    if request.agent_type == "maintenance":
        result = await maintenance_agent.query(db, request.question)
    elif request.agent_type == "compliance":
        result = compliance_agent.query(request.question)
    elif request.agent_type == "rootcause":
        result = await rootcause_agent.analyze(db, request.question)
    else:
        result = knowledge_agent.query(request.question)

    chat_record = ChatHistory(
        user_id=current_user.id,
        session_id=session_id,
        question=request.question,
        answer=result["answer"],
        agent_type=result.get("agent_type", request.agent_type),
        confidence=result.get("confidence", 0.0),
        sources=[s if isinstance(s, dict) else {} for s in result.get("sources", [])],
    )
    db.add(chat_record)

    logger.info(f"Chat query by {current_user.email}: {request.question[:80]}...")

    return ChatResponse(
        answer=result["answer"],
        confidence=result.get("confidence", 0.0),
        risk_level=result.get("risk_level", "low"),
        severity=result.get("severity", "low"),
        recommended_action=result.get("recommended_action", ""),
        sources=[CitationSource(**s) if isinstance(s, dict) else s for s in result.get("sources", [])],
        suggested_questions=result.get("suggested_questions", []),
        agent_type=result.get("agent_type", request.agent_type),
    )


@router.post("/maintenance/query", response_model=ChatResponse)
async def maintenance_query(
    request: MaintenanceQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await maintenance_agent.query(db, request.question, request.machine_id)

    chat_record = ChatHistory(
        user_id=current_user.id,
        session_id=generate_session_id(),
        question=request.question,
        answer=result["answer"],
        agent_type="maintenance",
        confidence=result.get("confidence", 0.0),
        sources=result.get("sources", []),
    )
    db.add(chat_record)

    return ChatResponse(
        answer=result["answer"],
        confidence=result.get("confidence", 0.0),
        risk_level=result.get("risk_level", "medium"),
        severity=result.get("severity", "medium"),
        recommended_action=result.get("recommended_action", ""),
        sources=[CitationSource(**s) if isinstance(s, dict) else s for s in result.get("sources", [])],
        suggested_questions=result.get("suggested_questions", []),
        agent_type="maintenance",
    )


@router.post("/compliance/query", response_model=ChatResponse)
async def compliance_query(
    request: ComplianceQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = compliance_agent.query(request.question)

    chat_record = ChatHistory(
        user_id=current_user.id,
        session_id=generate_session_id(),
        question=request.question,
        answer=result["answer"],
        agent_type="compliance",
        confidence=result.get("confidence", 0.0),
        sources=result.get("sources", []),
    )
    db.add(chat_record)

    return ChatResponse(
        answer=result["answer"],
        confidence=result.get("confidence", 0.0),
        risk_level=result.get("risk_level", "low"),
        severity=result.get("severity", "medium"),
        recommended_action=result.get("recommended_action", ""),
        sources=[CitationSource(**s) if isinstance(s, dict) else s for s in result.get("sources", [])],
        suggested_questions=result.get("suggested_questions", []),
        agent_type="compliance",
    )


@router.post("/emergency/query", response_model=EmergencyResponse)
async def emergency_query(
    request: EmergencyQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = emergency_agent.query(request.question)

    chat_record = ChatHistory(
        user_id=current_user.id,
        session_id=generate_session_id(),
        question=request.question,
        answer=result["answer"],
        agent_type="emergency",
        confidence=result.get("confidence", 0.0),
        sources=[s if isinstance(s, dict) else {} for s in result.get("sources", [])],
    )
    db.add(chat_record)

    logger.warning(f"Emergency query by {current_user.email}: {request.question}")

    return EmergencyResponse(
        is_emergency=result.get("is_emergency", False),
        answer=result["answer"],
        emergency_sop=result.get("emergency_sop", ""),
        shutdown_steps=result.get("shutdown_steps", []),
        ppe_required=result.get("ppe_required", []),
        emergency_contacts=result.get("emergency_contacts", []),
        sources=[CitationSource(**s) if isinstance(s, dict) else s for s in result.get("sources", [])],
        severity=result.get("severity", "critical"),
    )


@router.get("/chat/history")
async def get_chat_history(
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(ChatHistory).where(ChatHistory.user_id == current_user.id)
    if session_id:
        query = query.where(ChatHistory.session_id == session_id)
    query = query.order_by(desc(ChatHistory.timestamp)).limit(limit)

    result = await db.execute(query)
    histories = result.scalars().all()

    return {
        "success": True,
        "conversations": [ChatHistoryResponse.model_validate(h) for h in histories],
    }
