# Features

## Core Features

### 🔐 Authentication & Authorization
- JWT-based login/logout
- Role-based access: Admin, Plant Manager, Maintenance Engineer, Production Engineer, Safety Officer, Viewer
- Bcrypt password hashing
- Protected API endpoints

### 📄 Document Management
- Drag-and-drop upload (PDF, DOCX, TXT, PNG, JPG)
- Automatic text extraction (PyMuPDF)
- OCR for scanned documents (PaddleOCR)
- Auto-categorization and metadata extraction
- Search and filter documents
- Document versioning support

### 🤖 AI Knowledge Assistant
- Natural language Q&A powered by RAG
- Context-aware responses with source citations
- Conversation history
- Suggested follow-up questions
- Multiple agent modes (Knowledge, Maintenance, Compliance, Root Cause)

### 🔗 Knowledge Graph
- Interactive graph visualization
- Nodes: Machines, Documents, Engineers, Failures, SOPs, Vendors, Spare Parts
- Auto-updated on document upload
- Click-to-inspect node details
- Filter by entity type

### 🔧 Maintenance Intelligence
- Machine cards with health scores
- Maintenance log timeline
- Failure history analysis
- AI-powered repair recommendations
- Spare parts suggestions

### ✅ Compliance Assistant
- Compliance score tracking by area
- AI-generated safety checklists
- Regulatory guidance search
- SOP lookup

### 📊 Analytics Dashboard
- Plant Health Score (0-100) with trend
- KPI cards (documents, machines, AI queries, alerts)
- Charts: document categories, upload trends, machine health, failure trends
- Maintenance statistics (downtime, costs)

## Premium Features

### 🏥 AI Plant Health Score
Composite score (0-100) calculated from:
- Machine health (35%)
- Failure rate (25%)
- Maintenance compliance (20%)
- Knowledge coverage (20%)

### 🚨 Emergency Mode
Detects emergency keywords and instantly provides:
- Emergency SOP
- Shutdown sequence
- PPE requirements
- Emergency contacts

### 🧠 AI Decision Center
Every AI response includes:
- Confidence score
- Risk level
- Severity assessment
- Recommended action
- Supporting documents
