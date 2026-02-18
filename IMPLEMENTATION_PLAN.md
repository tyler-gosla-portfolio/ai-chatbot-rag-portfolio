# Implementation Plan

## Source: docs/DESIGN.reconciled.md

## Phase 1: Backend Foundation

### 1.1 Project Setup
- Initialize Python project with `pyproject.toml`
- Dependencies: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, python-jose[cryptography], argon2-cffi, openai, tiktoken, boto3, redis, python-multipart, pymupdf, python-docx
- Dev dependencies: pytest, pytest-asyncio, httpx, pytest-cov, ruff
- Create `backend/` directory structure:
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py              # FastAPI app factory
  │   ├── config.py            # Pydantic settings
  │   ├── database.py          # Async SQLAlchemy engine/session
  │   ├── models/              # SQLAlchemy ORM models
  │   │   ├── __init__.py
  │   │   ├── user.py
  │   │   ├── document.py
  │   │   ├── chunk.py
  │   │   ├── conversation.py
  │   │   └── message.py
  │   ├── schemas/             # Pydantic request/response schemas
  │   │   ├── __init__.py
  │   │   ├── auth.py
  │   │   ├── document.py
  │   │   ├── conversation.py
  │   │   └── message.py
  │   ├── api/                 # Route handlers
  │   │   ├── __init__.py
  │   │   ├── deps.py          # Dependency injection (get_db, get_current_user)
  │   │   ├── auth.py
  │   │   ├── documents.py
  │   │   ├── conversations.py
  │   │   ├── messages.py
  │   │   └── health.py
  │   ├── services/            # Business logic
  │   │   ├── __init__.py
  │   │   ├── auth.py
  │   │   ├── document.py
  │   │   ├── rag.py
  │   │   └── chat.py
  │   └── utils/
  │       ├── __init__.py
  │       └── security.py      # JWT + password hashing
  ├── alembic/
  │   ├── env.py
  │   └── versions/
  ├── alembic.ini
  ├── tests/
  │   ├── conftest.py
  │   ├── unit/
  │   │   ├── test_chunking.py
  │   │   ├── test_auth_utils.py
  │   │   └── test_rag_assembly.py
  │   └── integration/
  │       ├── test_auth_flow.py
  │       ├── test_document_flow.py
  │       └── test_chat_flow.py
  └── pyproject.toml
  ```

### 1.2 Database Models
- SQLAlchemy async models matching the schema in DESIGN.reconciled.md
- Users, Documents, Chunks, Conversations, ConversationDocuments, Messages
- pgvector column for chunk embeddings (vector(1536))

### 1.3 Alembic Migrations
- Initial migration creating all tables and indexes
- HNSW vector index on chunks.embedding

## Phase 2: Backend Core Features

### 2.1 Auth System
- POST /api/v1/auth/register — Argon2id password hashing
- POST /api/v1/auth/login — JWT access token (15min) + refresh token (7-day, HTTP-only cookie)
- POST /api/v1/auth/refresh — Rotate refresh token
- POST /api/v1/auth/logout — Revoke refresh token
- GET /api/v1/auth/me — Current user profile
- Dependency: `get_current_user` extracts user from JWT

### 2.2 Document Management
- POST /api/v1/documents/ — Multipart upload, validate MIME, store file (local for dev)
- GET /api/v1/documents/ — List with pagination and status filter
- GET /api/v1/documents/{id} — Single document with chunk stats
- DELETE /api/v1/documents/{id} — Delete document + chunks + file
- POST /api/v1/documents/{id}/reprocess — Re-chunk and re-embed

### 2.3 RAG Pipeline
- Text extraction: PyMuPDF (PDF), python-docx (DOCX), raw read (TXT/MD)
- Chunking: RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
- Embedding: OpenAI text-embedding-3-small (1536 dims)
- Vector search: cosine similarity, top-k=5, threshold > 0.72
- Prompt assembly with context and citations

### 2.4 Conversations & Messages
- CRUD for conversations with document attachment
- POST message → embed query → retrieve chunks → assemble prompt → stream response
- SSE streaming via FastAPI StreamingResponse
- Message feedback (thumbs up/down)

### 2.5 Health Endpoints
- GET /health — Liveness
- GET /health/ready — DB connectivity check

## Phase 3: Frontend

### 3.1 Next.js Setup
- Next.js 14 with App Router
- Tailwind CSS + shadcn/ui components
- TypeScript throughout

### 3.2 Auth Pages
- Login and Register forms
- Token management in memory + HTTP-only cookie refresh
- Protected route middleware

### 3.3 Dashboard Layout
- Sidebar with conversation list
- Header with user menu
- Responsive mobile navigation

### 3.4 Chat Interface
- ChatPanel with message list
- MessageBubble with citations
- MessageInput with send button
- StreamingIndicator
- SSE integration for streaming

### 3.5 Document Manager
- Upload dropzone (drag-and-drop)
- Document table with status badges
- Processing status indicator

## Phase 4: Testing

### 4.1 Backend Tests
- Unit: chunking, auth utils, RAG prompt assembly
- Integration: auth flow, document upload, chat flow
- Mocked OpenAI API calls

### 4.2 Frontend Tests
- Component tests with Vitest + Testing Library
- Hook tests (useChat, useAuth)

## Phase 5: Documentation & Delivery

### 5.1 README Update
- Setup instructions (backend + frontend)
- Environment variable reference
- How to run tests
- Project overview

### 5.2 Git & PR
- Commit to `review/claude-build`
- Push and open PR against `main`
