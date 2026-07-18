from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


# ===== Auth Schemas =====

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool = True
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: int = 1

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str
    password: str = Field(min_length=6)
    role: str = "viewer"


# ===== Document Schemas =====

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    title: str
    file_type: str
    file_size: int
    category: str
    tags: List[str] = []
    machine_name: str
    department: str
    version: str
    page_count: int
    processing_status: str
    ocr_confidence: float
    chunk_count: int
    uploaded_by: Optional[int] = None
    upload_date: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    success: bool = True
    total: int
    documents: List[DocumentResponse]


# ===== Chat Schemas =====

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = None
    agent_type: str = "knowledge"


class CitationSource(BaseModel):
    document: str
    page: Optional[int] = None
    chunk_text: str = ""
    relevance_score: float = 0.0


class ChatResponse(BaseModel):
    success: bool = True
    answer: str
    confidence: float = 0.0
    risk_level: str = "low"
    severity: str = "low"
    recommended_action: str = ""
    sources: List[CitationSource] = []
    suggested_questions: List[str] = []
    agent_type: str = "knowledge"


class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    agent_type: str
    confidence: float
    sources: List[Any] = []
    timestamp: datetime

    class Config:
        from_attributes = True


# ===== Machine Schemas =====

class MachineResponse(BaseModel):
    id: int
    name: str
    machine_type: str
    manufacturer: str
    model_number: str
    serial_number: str
    location: str
    department: str
    installation_date: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    status: str
    health_score: float
    operating_hours: int
    specifications: dict = {}

    class Config:
        from_attributes = True


class MachineListResponse(BaseModel):
    success: bool = True
    total: int
    machines: List[MachineResponse]


# ===== Maintenance Schemas =====

class MaintenanceLogResponse(BaseModel):
    id: int
    machine_id: int
    issue: str
    issue_type: str
    severity: str
    action_taken: str
    engineer: str
    spare_parts_used: List[str] = []
    downtime_hours: float
    cost: float
    status: str
    date: datetime
    resolved_date: Optional[datetime] = None
    notes: str

    class Config:
        from_attributes = True


class MaintenanceQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    machine_id: Optional[int] = None


# ===== Compliance Schemas =====

class ComplianceQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


# ===== Emergency Schemas =====

class EmergencyQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    machine_id: Optional[int] = None


class EmergencyResponse(BaseModel):
    success: bool = True
    is_emergency: bool = False
    answer: str
    emergency_sop: str = ""
    shutdown_steps: List[str] = []
    ppe_required: List[str] = []
    emergency_contacts: List[dict] = []
    sources: List[CitationSource] = []
    severity: str = "low"


# ===== Dashboard Schemas =====

class DashboardStats(BaseModel):
    total_documents: int = 0
    documents_today: int = 0
    active_machines: int = 0
    total_machines: int = 0
    ai_queries_today: int = 0
    critical_alerts: int = 0
    compliance_score: float = 0.0
    plant_health_score: float = 0.0
    recent_uploads: List[DocumentResponse] = []
    recent_conversations: List[ChatHistoryResponse] = []


class HealthScoreResponse(BaseModel):
    success: bool = True
    overall_score: float = 0.0
    breakdown: dict = {}
    trend: str = "stable"
    recommendations: List[str] = []


# ===== Analytics Schemas =====

class AnalyticsResponse(BaseModel):
    success: bool = True
    documents_by_category: dict = {}
    upload_trends: List[dict] = []
    machine_health: List[dict] = []
    ai_usage: dict = {}
    failure_trends: List[dict] = []
    top_searched_equipment: List[dict] = []
    maintenance_stats: dict = {}


# ===== Knowledge Graph Schemas =====

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    properties: dict = {}


class GraphResponse(BaseModel):
    success: bool = True
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []


# ===== Error Schema =====

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str = "UNKNOWN"


# Fix forward reference
LoginResponse.model_rebuild()
