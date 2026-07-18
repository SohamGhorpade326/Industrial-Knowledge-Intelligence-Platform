# API Documentation

## Base URL

`http://localhost:8000/api`

## Authentication

All endpoints except `/api/auth/login` require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### POST `/api/auth/login`
Login and receive JWT token.

**Request:**
```json
{ "email": "admin@ikp.com", "password": "admin123" }
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "name": "Admin User", "email": "admin@ikp.com", "role": "admin" }
}
```

### POST `/api/auth/register`
Register a new user.

### POST `/api/auth/logout`
Logout current user.

### GET `/api/auth/me`
Get current authenticated user.

---

## Upload Endpoints

### POST `/api/upload`
Upload a document (multipart form data).

**Form Fields:**
- `file` (required): Document file (PDF, DOCX, TXT, PNG, JPG)
- `category`: Document category
- `machine_name`: Associated machine
- `department`: Department
- `tags`: Comma-separated tags

---

## Document Endpoints

### GET `/api/documents`
List documents with optional filters.

**Query Parameters:** `category`, `machine_name`, `search`, `limit`, `offset`

### GET `/api/documents/{id}`
Get document by ID.

### DELETE `/api/documents/{id}`
Delete document and its embeddings.

---

## AI Chat Endpoints

### POST `/api/chat`
Send a message to the AI assistant.

**Request:**
```json
{
  "question": "What is the startup procedure for the CNC Machine?",
  "agent_type": "knowledge",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Based on the SOP manual...",
  "confidence": 85.5,
  "risk_level": "low",
  "severity": "low",
  "recommended_action": "...",
  "sources": [{ "document": "cnc_sop.pdf", "page": 3, "chunk_text": "...", "relevance_score": 0.89 }],
  "suggested_questions": ["...", "...", "..."],
  "agent_type": "knowledge"
}
```

### POST `/api/maintenance/query`
Maintenance-specific query with optional machine context.

### POST `/api/compliance/query`
Compliance and safety query.

### POST `/api/emergency/query`
Emergency response query (detects emergency keywords).

### GET `/api/chat/history`
Get chat history for current user.

---

## Dashboard Endpoints

### GET `/api/dashboard`
Get dashboard statistics.

### GET `/api/dashboard/health-score`
Get plant health score with breakdown.

---

## Analytics Endpoints

### GET `/api/analytics`
Get comprehensive analytics data (documents by category, upload trends, machine health, AI usage, failure trends, maintenance stats).

---

## Maintenance Endpoints

### GET `/api/maintenance/machines`
List all machines.

### GET `/api/maintenance/machines/{id}`
Get machine details.

### GET `/api/maintenance/logs`
Get maintenance logs (optional `machine_id` filter).

### GET `/api/maintenance/timeline/{machine_id}`
Get machine maintenance timeline.

### GET `/api/maintenance/failures/{machine_id}`
Get failure history for a machine.

---

## Knowledge Graph Endpoints

### GET `/api/graph`
Get full knowledge graph (nodes and edges).

### GET `/api/graph/machine/{machine_name}`
Get subgraph for a specific machine.

---

## Compliance Endpoints

### POST `/api/compliance/query`
Query compliance documents.

### POST `/api/compliance/checklist`
Generate AI compliance checklist.

---

## Health Check

### GET `/api/health`
Application health check (no auth required).

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE"
}
```
