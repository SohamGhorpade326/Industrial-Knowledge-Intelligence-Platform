from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    PLANT_MANAGER = "plant_manager"
    MAINTENANCE_ENGINEER = "maintenance_engineer"
    PRODUCTION_ENGINEER = "production_engineer"
    SAFETY_OFFICER = "safety_officer"
    VIEWER = "viewer"


class DocumentCategory(str, Enum):
    SOP = "sop"
    MAINTENANCE_MANUAL = "maintenance_manual"
    SAFETY_MANUAL = "safety_manual"
    INSPECTION_REPORT = "inspection_report"
    CALIBRATION_CERTIFICATE = "calibration_certificate"
    INCIDENT_REPORT = "incident_report"
    VENDOR_MANUAL = "vendor_manual"
    SHIFT_LOG = "shift_log"
    COMPLIANCE_DOCUMENT = "compliance_document"
    GENERAL = "general"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"


class MachineStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    IDLE = "idle"
    DECOMMISSIONED = "decommissioned"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
TOP_K_RESULTS = 5

EMERGENCY_KEYWORDS = [
    "fire", "explosion", "gas leak", "overheating", "electrical fault",
    "chemical spill", "pressure failure", "steam leak", "toxic",
    "emergency", "shutdown", "danger", "hazard", "critical failure"
]

GRAPH_NODE_TYPES = [
    "Machine", "Document", "Engineer", "Failure",
    "SOP", "Vendor", "SparePart", "Inspection", "MaintenanceTask"
]

GRAPH_RELATIONSHIPS = [
    "HAS_DOCUMENT", "FAILED_WITH", "RESOLVED_BY", "PERFORMED",
    "MAINTAINED_BY", "LOCATED_IN", "REFERENCES", "HAS_SPARE", "INSPECTED"
]
