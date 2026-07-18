export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  access_token: string;
  token_type: string;
  user: User;
}

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  title: string;
  file_type: string;
  file_size: number;
  category: string;
  tags: string[];
  machine_name: string;
  department: string;
  version: string;
  page_count: number;
  processing_status: string;
  ocr_confidence: number;
  chunk_count: number;
  uploaded_by: number | null;
  upload_date: string;
}

export interface CitationSource {
  document: string;
  page: number | null;
  chunk_text: string;
  relevance_score: number;
}

export interface ChatMessage {
  id?: number;
  question: string;
  answer: string;
  agent_type: string;
  confidence: number;
  risk_level: string;
  severity: string;
  recommended_action: string;
  sources: CitationSource[];
  suggested_questions: string[];
  timestamp?: string;
  isUser?: boolean;
}

export interface EmergencyResponse {
  success: boolean;
  is_emergency: boolean;
  answer: string;
  emergency_sop: string;
  shutdown_steps: string[];
  ppe_required: string[];
  emergency_contacts: EmergencyContact[];
  sources: CitationSource[];
  severity: string;
}

export interface EmergencyContact {
  name: string;
  phone: string;
  role: string;
}

export interface Machine {
  id: number;
  name: string;
  machine_type: string;
  manufacturer: string;
  model_number: string;
  serial_number: string;
  location: string;
  department: string;
  installation_date: string | null;
  last_maintenance_date: string | null;
  status: string;
  health_score: number;
  operating_hours: number;
  specifications: Record<string, any>;
}

export interface MaintenanceLog {
  id: number;
  machine_id: number;
  issue: string;
  issue_type: string;
  severity: string;
  action_taken: string;
  engineer: string;
  spare_parts_used: string[];
  downtime_hours: number;
  cost: number;
  status: string;
  date: string;
  resolved_date: string | null;
  notes: string;
}

export interface DashboardStats {
  total_documents: number;
  documents_today: number;
  active_machines: number;
  total_machines: number;
  ai_queries_today: number;
  critical_alerts: number;
  compliance_score: number;
  plant_health_score: number;
  recent_uploads: Document[];
  recent_conversations: ChatMessage[];
}

export interface HealthScore {
  overall_score: number;
  breakdown: {
    machine_health: number;
    failure_rate: number;
    maintenance_compliance: number;
    knowledge_coverage: number;
  };
  trend: string;
  recommendations: string[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  properties: Record<string, any>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AnalyticsData {
  documents_by_category: Record<string, number>;
  upload_trends: { date: string; count: number }[];
  machine_health: { name: string; health_score: number; status: string }[];
  ai_usage: { total_queries: number; agent_breakdown: Record<string, number> };
  failure_trends: { severity: string; count: number }[];
  top_searched_equipment: { name: string; queries: number }[];
  maintenance_stats: { total_records: number; avg_downtime_hours: number; total_cost: number };
}

export type ThemeMode = 'dark' | 'light';
