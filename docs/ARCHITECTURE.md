# Architecture

## System Architecture

The Industrial Knowledge Intelligence Platform follows a modular, layered architecture:

### 1. Presentation Layer (Frontend)
- **React 18** with TypeScript for type safety
- **Material UI** for enterprise-grade components
- **TailwindCSS** for responsive layouts
- **Framer Motion** for smooth animations
- **Chart.js** for data visualization
- **Zustand** for state management

### 2. API Layer (Backend)
- **FastAPI** with async endpoints
- **JWT Authentication** with role-based access control
- **Pydantic** for request/response validation
- **CORS** middleware for frontend integration

### 3. Business Logic Layer (Services)
- **Document Service**: Upload, parse, OCR, chunk, embed
- **RAG Service**: Retrieval-Augmented Generation pipeline
- **Embedding Service**: Vector generation and similarity search
- **Graph Service**: Neo4j knowledge graph operations
- **Analytics Service**: Dashboard stats and health score computation

### 4. AI Agent Layer
- **Knowledge Agent**: General document Q&A
- **Maintenance Agent**: Equipment-specific analysis
- **Compliance Agent**: Safety and regulatory queries
- **Emergency Agent**: Critical situation response
- **Root Cause Agent**: Failure analysis with 5-Why methodology

### 5. Data Layer
- **SQLite**: Users, documents, machines, maintenance logs, chat history
- **ChromaDB**: Vector embeddings for semantic search
- **Neo4j**: Knowledge graph of equipment relationships

## Data Flow

### Document Ingestion Pipeline
```
Upload → File Validation → Text Extraction (PyMuPDF) → OCR (PaddleOCR, if needed) → Text Chunking (600 tokens, 100 overlap) → Embedding (BAAI/bge-small-en-v1.5) → ChromaDB Storage → Neo4j Graph Update
```

### AI Query Pipeline (RAG)
```
User Question → Query Embedding → ChromaDB Similarity Search (Top-5) → Context Assembly → Groq LLM (Llama 3.3 70B) → Answer + Citations → Response with Confidence Score
```

### Authentication Flow
```
Login Request → Password Verification (bcrypt) → JWT Token Generation → Token in Header → Middleware Validation → User Context Injection
```

## Design Decisions

1. **Async FastAPI**: All database and AI operations are non-blocking
2. **Singleton Services**: Embedding model and DB connections are initialized once
3. **Graceful Fallbacks**: App works without Neo4j or PaddleOCR
4. **Modular Agents**: Each AI agent has a specialized prompt and data pipeline
5. **Composite Health Score**: Weighted average of machine health, failure rate, maintenance compliance, and knowledge coverage
