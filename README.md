# AI Chatbot with RAG Portfolio Project

A full-stack AI chatbot with Retrieval-Augmented Generation (RAG) capabilities.
Upload documents (PDF, TXT, MD, DOCX) and chat with an AI that uses your content as context.

## Tech Stack

- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (async), Pydantic v2
- **Database:** PostgreSQL + pgvector (production), SQLite (testing)
- **AI:** OpenAI API (text-embedding-3-small + GPT-4o), RAG pipeline
- **Auth:** JWT access tokens, Argon2id password hashing
- **Deployment:** Vercel (frontend), Railway (backend + DB)

## Features

- [x] User authentication (register, login, JWT)
- [x] Document upload (PDF, TXT, MD, DOCX)
- [x] RAG pipeline: chunking, embedding, vector search
- [x] Context-aware chat with source citations
- [x] Conversation management (create, list, delete)
- [x] Message feedback (thumbs up/down)
- [x] Health check endpoints
- [x] Responsive dashboard with sidebar navigation

## Project Structure

```
├── frontend/                # Next.js 14 application
│   ├── src/
│   │   ├── app/             # App Router pages (auth, dashboard, chat)
│   │   ├── components/      # React components (chat, documents, layout)
│   │   ├── hooks/           # Custom hooks (useAuth, useChat, useDocuments)
│   │   ├── lib/             # API client, utilities
│   │   └── types/           # TypeScript interfaces
│   └── __tests__/           # Vitest + Testing Library tests
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── api/             # Route handlers (auth, documents, conversations, messages, health)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic (RAG, chat, document processing)
│   │   └── utils/           # Security (JWT, Argon2id)
│   └── tests/               # pytest + pytest-asyncio tests
├── docs/                    # Design documents
└── IMPLEMENTATION_PLAN.md   # Build plan
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (production) or SQLite (development/testing)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Create .env file (optional - defaults work for testing)
cat > .env << EOF
TESTING=false
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot_rag
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET=change-this-to-a-long-random-string
EOF

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

### Running Tests

#### Backend Tests (35 tests)

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

Tests use SQLite (via aiosqlite) and mock OpenAI responses — no external services required.

#### Frontend Tests (11 tests)

```bash
cd frontend
npx vitest run
```

### API Endpoints

| Group | Endpoint | Description |
|-------|----------|-------------|
| Auth | `POST /api/v1/auth/register` | Create account |
| Auth | `POST /api/v1/auth/login` | Get JWT token |
| Auth | `GET /api/v1/auth/me` | Current user |
| Documents | `POST /api/v1/documents/` | Upload document |
| Documents | `GET /api/v1/documents/` | List documents |
| Documents | `DELETE /api/v1/documents/{id}` | Delete document |
| Conversations | `POST /api/v1/conversations/` | Create conversation |
| Conversations | `GET /api/v1/conversations/` | List conversations |
| Messages | `POST /api/v1/conversations/{id}/messages/` | Send message (triggers RAG) |
| Messages | `GET /api/v1/conversations/{id}/messages/` | Message history |
| Health | `GET /health` | Liveness probe |
| Health | `GET /health/ready` | Readiness probe |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async database connection |
| `OPENAI_API_KEY` | `sk-test` | OpenAI API key (mock responses with `sk-test`) |
| `JWT_SECRET` | dev default | Secret for signing JWT tokens |
| `UPLOAD_DIR` | `uploads` | Local file storage directory |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

---

Built to demonstrate full-stack AI development capabilities.
