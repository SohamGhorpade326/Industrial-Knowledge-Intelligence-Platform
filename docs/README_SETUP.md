# Setup Guide

## Detailed Installation Instructions

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10+ | 3.12+ |
| Node.js | 18+ | 20+ |
| RAM | 4 GB | 8 GB+ |
| Storage | 2 GB | 5 GB+ |
| OS | Windows 10/Linux/macOS | Any |

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd ET-2.0
```

### Step 2: Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and set your `GROQ_API_KEY`. Get one free at https://console.groq.com

### Step 3: Backend Setup

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will:
1. Create the SQLite database
2. Seed sample users, machines, and maintenance logs
3. Initialize ChromaDB vector store
4. Start the API at http://localhost:8000

### Step 4: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will start at http://localhost:5173

### Step 5: Login

Navigate to http://localhost:5173 and login with:
- **Email**: admin@ikp.com
- **Password**: admin123

### Optional: Neo4j Setup

For full knowledge graph functionality:

1. Download Neo4j Community: https://neo4j.com/download/
2. Start Neo4j and set password to `password`
3. Update `.env` if using different credentials

Without Neo4j, the Knowledge Graph page will show sample/fallback data.

### Docker Deployment

```bash
# Build and start all services
docker compose up --build

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Neo4j: http://localhost:7474
```

## Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@ikp.com | admin123 | Admin |
| rajesh@ikp.com | rajesh123 | Maintenance Engineer |
| priya@ikp.com | priya123 | Safety Officer |
| amit@ikp.com | amit123 | Plant Manager |
| sneha@ikp.com | sneha123 | Production Engineer |
| viewer@ikp.com | viewer123 | Viewer |

## Troubleshooting

### PaddleOCR Installation Issues
If PaddleOCR fails to install, the app will still work — OCR features will be disabled. Text-based PDFs will still be processed normally.

### ChromaDB Errors
Ensure the `vector_db/` directory exists and is writable. The app creates it automatically.

### Groq API Errors
Verify your `GROQ_API_KEY` is valid and has available quota. The app will show informative error messages when AI features are unavailable.
