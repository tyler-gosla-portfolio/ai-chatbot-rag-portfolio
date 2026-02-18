# RECONCILED DESIGN


Changelog:
- Merged Claude suggestions for caching, S3, HNSW, Argon2id, and testing.
- Kept original repo structure and WebSocket streaming.


# AI Chatbot with RAG - Alternate Design Document

> Alternate design by Claude — not a replacement for the original.

---

## 1. System Architecture

### Overview

A three-tier architecture: SPA frontend, async Python API, and PostgreSQL with vector extensions. The RAG pipeline runs as an async background task triggered by API calls.

```
┌──────────────────────────────────┐
│          Browser (SPA)           │
│  Next.js 14 · App Router · SSR  │
└──────────────┬───────────────────┘
               │ HTTPS / WSS
┌──────────────▼───────────────────┐
│          API Server              │
│  FastAPI · async · Uvicorn       │
│                                  │
│  ┌───────┐ ┌──────┐ ┌────────┐  │
│  │ Auth  │ │ CRUD │ │  RAG   │  │
│  │ Midw. │ │Routes│ │ Engine │  │
│  └───┬───┘ └──┬───┘ └───┬────┘  │
│      │        │         │        │
│  ┌───▼────────▼─────────▼─────┐  │
│  │     Service Layer          │  │
│  │  (business logic, queue)   │  │
│  └────────────┬───────────────┘  │
└───────────────┼──────────────────┘
                │
     ┌──────────┼──────────┐
     │          │          │
┌────▼───┐ ┌───▼────┐ ┌───▼──────┐
│Postgres│ │ Redis  │ │ OpenAI   │
│+pgvect.│ │(cache, │ │ API      │
│        │ │ queue) │ │(GPT-4o,  │
└────────┘ └────────┘ │embed-3)  │
                      └──────────┘
```

### Key Differences from Monolithic

| Concern | Approach |
|---------|----------|
| Background jobs | Redis + Celery (or `arq`) for document processing |
| Caching | Redis for session cache and rate-limit counters |
| Streaming | Server-Sent Events (SSE) via FastAPI `StreamingResponse` |
| File storage | S3-compatible (MinIO locally, Cloudflare R2 in prod) |

---

## 2. Database Schema

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(320) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(127) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    s3_key TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','processing','ready','failed')),
    error_message TEXT,
    chunk_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Chunks (with embeddings)
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    token_count INT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    model TEXT NOT NULL DEFAULT 'gpt-4o',
    system_prompt TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Conversation-Document link (many-to-many)
CREATE TABLE conversation_documents (
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    PRIMARY KEY (conversation_id, document_id)
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('system','user','assistant')),
    content TEXT NOT NULL,
    token_count INT,
    latency_ms INT,
    model TEXT,
    sources JSONB DEFAULT '[]',
    feedback SMALLINT CHECK (feedback IN (-1, 0, 1)),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_chunks_doc ON chunks(document_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_messages_convo ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(conversation_id, created_at);

-- HNSW vector index (preferred over IVFFlat for <1M rows)
CREATE INDEX idx_chunks_embedding ON chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Schema Differences from Original

- Uses `HNSW` index instead of `IVFFlat` — no need for periodic re-training
- Adds `s3_key` for external file storage instead of local `file_path`
- Adds `feedback` column on messages for thumbs-up/down
- Uses composite PK on junction table instead of surrogate UUID
- `email` field uses VARCHAR(320) per RFC 5321 max length
- Adds `display_name`, `is_active`, `error_message`, `model`, `system_prompt`

---

## 3. API Endpoints

### Auth (`/api/v1/auth`)

```
POST   /register          — Create account (email, password, display_name)
POST   /login             — Get access + refresh tokens
POST   /refresh           — Rotate refresh token
POST   /logout            — Revoke refresh token
GET    /me                — Current user profile
```

### Documents (`/api/v1/documents`)

```
POST   /                  — Upload document (multipart/form-data)
GET    /                  — List documents (paginated, ?status=ready)
GET    /{id}              — Single document with chunk stats
GET    /{id}/chunks       — List chunks for a document (paginated)
DELETE /{id}              — Delete document + chunks + S3 object
POST   /{id}/reprocess    — Re-chunk and re-embed a document
```

### Conversations (`/api/v1/conversations`)

```
POST   /                  — Create conversation (attach document_ids)
GET    /                  — List conversations (paginated, sorted)
GET    /{id}              — Conversation with recent messages
PATCH  /{id}              — Update title, system_prompt, attached docs
DELETE /{id}              — Delete conversation + messages
```

### Messages (`/api/v1/conversations/{id}/messages`)

```
POST   /                  — Send message, get AI response
GET    /                  — Paginated history (?before=<cursor>)
GET    /stream            — SSE endpoint for streaming response
POST   /{msg_id}/feedback — Submit thumbs-up/down
```

### Health & Admin

```
GET    /health             — Liveness probe
GET    /health/ready       — Readiness (DB + OpenAI reachable)
GET    /metrics            — Prometheus-format metrics
```

---

## 4. RAG Pipeline

### Ingestion Flow

```
Upload → Validate MIME → Store in S3
  → Enqueue background job
  → Extract text (PyMuPDF for PDF, python-docx for DOCX, raw for TXT/MD)
  → Clean text (normalize unicode, strip headers/footers)
  → Chunk with RecursiveCharacterTextSplitter
      - chunk_size: 500 tokens
      - chunk_overlap: 50 tokens
      - separators: ["\n\n", "\n", ". ", " "]
  → Batch embed via text-embedding-3-small (max 2048 tokens/chunk)
  → INSERT chunks + embeddings
  → UPDATE document status → 'ready'
```

### Query Flow

```
User message
  → Embed query with text-embedding-3-small
  → Cosine similarity search: top-k=5, threshold > 0.72
  → Re-rank with cross-encoder (optional, ms-marco-MiniLM-L-6-v2)
  → Assemble prompt:
      SYSTEM: You are a helpful assistant. Answer based on the provided context.
              If unsure, say so. Cite sources by [doc:chunk_index].
      CONTEXT: {top_k chunks with metadata}
      USER: {original query}
  → Stream response via GPT-4o
  → Parse citations from response
  → Store message + sources in DB
```

### Retrieval Tuning

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Top-k | 5 | Balances context window use vs. recall |
| Similarity threshold | 0.72 | Filters irrelevant chunks |
| Chunk size | 500 tokens | Preserves paragraph-level context |
| Overlap | 50 tokens | Prevents hard cuts mid-sentence |
| Embedding model | text-embedding-3-small | Cost-effective, 1536 dims |
| Completion model | gpt-4o | Best quality-to-cost for production |

---

## 5. Frontend Components

```
src/
├── app/
│   ├── layout.tsx                  # Root: providers, fonts, metadata
│   ├── page.tsx                    # Landing page / redirect
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── (dashboard)/
│       ├── layout.tsx              # Sidebar + header shell
│       ├── page.tsx                # Conversation list
│       ├── conversations/[id]/
│       │   └── page.tsx            # Chat view
│       └── documents/
│           └── page.tsx            # Document manager
├── components/
│   ├── chat/
│   │   ├── ChatPanel.tsx           # Main chat area
│   │   ├── MessageBubble.tsx       # Single message with citations
│   │   ├── MessageInput.tsx        # Textarea + send button
│   │   ├── StreamingIndicator.tsx  # Typing / loading animation
│   │   └── SourceCard.tsx          # Expandable source citation
│   ├── documents/
│   │   ├── UploadDropzone.tsx      # Drag-and-drop upload
│   │   ├── DocumentTable.tsx       # List with status badges
│   │   └── ProcessingStatus.tsx    # Real-time progress bar
│   └── layout/
│       ├── Sidebar.tsx             # Conversation list + new chat
│       ├── Header.tsx              # User menu, settings
│       └── MobileNav.tsx           # Responsive hamburger menu
├── hooks/
│   ├── useChat.ts                  # Send message, manage state
│   ├── useSSE.ts                   # EventSource for streaming
│   ├── useDocuments.ts             # CRUD + upload progress
│   └── useAuth.ts                  # Login, logout, token refresh
├── lib/
│   ├── api-client.ts               # Fetch wrapper with auth headers
│   ├── sse-client.ts               # SSE connection manager
│   └── format.ts                   # Date, file size formatters
└── types/
    ├── api.ts                      # Request/response types
    └── models.ts                   # Domain models
```

---

## 6. Security

### Authentication & Authorization

- **Access tokens**: JWT, HS256, 15-min expiry, stored in memory (not localStorage)
- **Refresh tokens**: opaque UUID, 7-day expiry, HTTP-only Secure SameSite=Strict cookie
- **Password storage**: Argon2id (preferred over bcrypt for GPU resistance)
- **Row-level access**: all queries filter by `user_id` from JWT claims

### Input Validation

- Pydantic v2 models on every endpoint
- File upload: validate MIME type server-side (not just extension)
- Max file size: 10 MB per document
- Max documents per user: 50 (configurable)

### Rate Limiting

| Endpoint group | Limit | Window |
|----------------|-------|--------|
| Auth | 5 req | 1 min |
| Document upload | 10 req | 1 hour |
| Chat messages | 30 req | 1 min |
| General API | 120 req | 1 min |

### Prompt Injection Mitigation

- System prompt is never user-editable in production
- User input placed in clearly delimited `<user_query>` tags
- Output is sanitized before rendering (no raw HTML from LLM)

---

## 7. Deployment

### Production Architecture

```
                  ┌─────────────┐
                  │  Cloudflare │
                  │  (DNS+CDN)  │
                  └──────┬──────┘
              ┌──────────┼──────────┐
              │          │          │
        ┌─────▼──┐  ┌───▼────┐  ┌─▼────────┐
        │ Vercel │  │Railway │  │Cloudflare │
        │  (FE)  │  │  (API) │  │  R2 (S3)  │
        └────────┘  └───┬────┘  └───────────┘
                        │
              ┌─────────┼─────────┐
              │         │         │
         ┌────▼──┐ ┌────▼──┐ ┌───▼───┐
         │ Neon  │ │ Redis │ │OpenAI │
         │(PG15) │ │(Upst.)│ │  API  │
         └───────┘ └───────┘ └───────┘
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Redis
REDIS_URL=redis://...

# OpenAI
OPENAI_API_KEY=sk-...

# Auth
JWT_SECRET=<64-char-random>
JWT_ALGORITHM=HS256

# Storage
S3_ENDPOINT=https://...
S3_BUCKET=rag-documents
S3_ACCESS_KEY=...
S3_SECRET_KEY=...

# App
FRONTEND_URL=https://chatbot.example.com
CORS_ORIGINS=["https://chatbot.example.com"]
LOG_LEVEL=info
```

### CI/CD

- GitHub Actions: lint, type-check, test on every PR
- Auto-deploy `main` to staging; manual promote to production
- DB migrations via Alembic run as a pre-deploy step

---

## 8. Testing Strategy

### Backend

| Layer | Tool | Coverage Target |
|-------|------|----------------|
| Unit | pytest + pytest-asyncio | 85% |
| Integration | TestClient + test DB | Key flows |
| RAG pipeline | Mocked OpenAI responses | Chunking, retrieval, assembly |
| Load | Locust | 100 concurrent users |

```
tests/
├── conftest.py                # DB fixtures, test client, mock OpenAI
├── unit/
│   ├── test_chunking.py       # Text splitting edge cases
│   ├── test_auth_utils.py     # Token creation/validation
│   └── test_rag_assembly.py   # Prompt construction
├── integration/
│   ├── test_auth_flow.py      # Register → login → refresh → logout
│   ├── test_document_flow.py  # Upload → process → query
│   └── test_chat_flow.py      # Create → message → stream → feedback
└── load/
    └── locustfile.py          # Concurrent chat + upload scenarios
```

### Frontend

| Layer | Tool | Coverage Target |
|-------|------|----------------|
| Component | Vitest + Testing Library | 70% |
| Integration | Playwright | Critical paths |
| Accessibility | axe-core | 0 violations |

```
__tests__/
├── components/
│   ├── ChatPanel.test.tsx
│   ├── MessageBubble.test.tsx
│   └── UploadDropzone.test.tsx
├── hooks/
│   ├── useChat.test.ts
│   └── useSSE.test.ts
└── e2e/
    ├── auth.spec.ts
    ├── upload-and-chat.spec.ts
    └── mobile-responsive.spec.ts
```

---

## Appendix: Key Design Decisions

1. **SSE over WebSocket** — Simpler to implement, works through all proxies/CDNs, sufficient for unidirectional streaming. User sends via POST, receives via SSE.

2. **HNSW over IVFFlat** — No need to periodically retrain the index. Better recall at small-to-medium scale. Slightly higher memory but worth the tradeoff.

3. **Argon2id over bcrypt** — More resistant to GPU/ASIC attacks. Recommended by OWASP as of 2024.

4. **S3-compatible storage over local filesystem** — Stateless API servers, works across horizontal scaling, cheap at rest.

5. **Redis for background jobs** — Enables async document processing without blocking the API. Also used for rate-limit counters and session cache.

6. **Cursor-based pagination over offset** — Stable pagination for chat messages even when new messages arrive.

7. **Feedback column on messages** — Enables future fine-tuning and quality monitoring with minimal schema overhead.
