# AI Chatbot with RAG - Design Document

## 1. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Next.js 14  │  │  React 18    │  │  TypeScript          │  │
│  │  (App Router)│  │  Components  │  │  Tailwind + shadcn   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          └─────────────────┼─────────────────────┘
                            │ HTTPS/WSS
┌───────────────────────────┼─────────────────────────────────────┐
│                      API GATEWAY                                │
│  ┌────────────────────────┼────────────────────────────────┐   │
│  │                   FastAPI Server                          │   │
│  │  ┌─────────────┐  ┌────┴────┐  ┌─────────────────────┐  │   │
│  │  │  Auth       │  │  API    │  │  WebSocket Handler  │  │   │
│  │  │  (JWT)      │  │  Routes │  │  (Streaming)        │  │   │
│  │  └─────────────┘  └────┬────┘  └─────────────────────┘  │   │
│  └────────────────────────┼────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
┌─────────▼─────────┐ ┌────▼────┐  ┌─────────▼──────────┐
│    AI SERVICES    │ │  RAG    │  │   DATA LAYER       │
│  ┌─────────────┐  │ │ Pipeline│  │  ┌──────────────┐  │
│  │ OpenAI API  │  │ │         │  │  │ PostgreSQL   │  │
│  │ - GPT-4     │  │ │ ┌─────┐ │  │  │ + pgvector   │  │
│  │ - Embeddings│  │ │ │Embed│ │  │  └──────────────┘  │
│  └─────────────┘  │ │ │Store│ │  └────────────────────┘
│                   │ │ ├─────┤ │
│                   │ │ │Chunk│ │
│                   │ │ ├─────┤ │
│                   │ │ │Index│ │
│                   │ │ └─────┘ │
│                   │ │ Retrieve│
│                   │ └────┬────┘
│                   └──────┼────────┐
│                          │        │
│                   ┌──────▼────┐   │
│                   │  Context  │   │
│                   │  Assembly │   │
│                   └───────────┘   │
└───────────────────────────────────┘
```

### Component Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Frontend** | Next.js 14 App | SSR, routing, API client |
| **Frontend** | React Components | UI rendering, state management |
| **Frontend** | TanStack Query | Server state, caching, mutations |
| **Backend** | FastAPI | HTTP API, WebSocket, auth middleware |
| **Backend** | SQLAlchemy | ORM, database operations |
| **AI** | OpenAI SDK | LLM completions, embeddings |
| **RAG** | LangChain/LlamaIndex | Chunking, retrieval, context assembly |
| **Storage** | PostgreSQL + pgvector | Document metadata, embeddings, chat history |

---

## 2. Technology Choices

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.x | React framework with App Router |
| React | 18.x | UI library with concurrent features |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Utility-first styling |
| shadcn/ui | latest | Pre-built accessible components |
| TanStack Query | 5.x | Server state management |
| Zustand | 4.x | Client state management |
| React Hook Form | 7.x | Form handling |
| Zod | 3.x | Schema validation |

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Primary language |
| FastAPI | 0.104+ | High-performance API framework |
| SQLAlchemy | 2.x | Async ORM |
| Alembic | 1.x | Database migrations |
| Pydantic | 2.x | Data validation |
| python-jose | 3.x | JWT handling |
| passlib | 1.x | Password hashing |
| websockets | 12.x | Real-time streaming |

### AI/ML Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| OpenAI Python SDK | 1.x | GPT-4 and embeddings API |
| tiktoken | 0.5.x | Token counting for chunking |
| LangChain | 0.1.x | RAG pipeline orchestration |

### Database & Infrastructure

| Technology | Purpose |
|------------|---------|
| PostgreSQL 15+ | Primary database |
| pgvector | Vector similarity search |
| Vercel | Frontend hosting |
| Railway/Render | Backend hosting |

---

## 3. Database Schema

### SQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'processing',
    chunk_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks with embeddings
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    token_count INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat sessions
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Many-to-many: chats can reference multiple documents
CREATE TABLE chat_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(chat_id, document_id)
);

-- Messages within chats
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER,
    latency_ms INTEGER,
    sources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_messages_chat_id ON messages(chat_id);

-- Vector similarity index
CREATE INDEX idx_chunks_embedding ON chunks 
    USING ivfflat (embedding vector_cosine_ops) 
    WITH (lists = 100);
```

---

## 4. API Design

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create new account |
| POST | `/api/v1/auth/login` | Authenticate, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Invalidate tokens |

### Document Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents` | Upload document |
| GET | `/api/v1/documents` | List user's documents |
| GET | `/api/v1/documents/{id}` | Get document details |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chats` | Create new chat |
| GET | `/api/v1/chats` | List user's chats |
| GET | `/api/v1/chats/{id}` | Get chat with messages |
| DELETE | `/api/v1/chats/{id}` | Delete chat |

### Message Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chats/{id}/messages` | Send message |
| GET | `/api/v1/chats/{id}/messages` | Get message history |
| WS | `/api/v1/chats/{id}/messages/stream` | WebSocket streaming |

---

## 5. RAG Pipeline Design

### Pipeline Flow

```
DOCUMENT INGESTION:
  1. Upload PDF/TXT/MD → Text extraction
  2. Clean & Chunk (512 tokens, 64 overlap)
  3. Embed with text-embedding-3-small
  4. Store in PostgreSQL with pgvector

QUERY PROCESSING:
  1. Receive user query
  2. Generate query embedding
  3. Similarity search (top 5 chunks)
  4. Assemble context
  5. Stream response via GPT-4
```

### Chunking Configuration

```python
chunk_size = 512        # tokens
chunk_overlap = 64      # tokens
separators = ["\n\n", "\n", " ", ""]
```

---

## 6. Frontend Component Hierarchy

```
app/
├── layout.tsx              # Root layout with providers
├── page.tsx                # Landing / dashboard
├── globals.css
│
├── (auth)/
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
│
├── (app)/
│   ├── layout.tsx          # App shell with sidebar
│   ├── page.tsx            # Chat list / dashboard
│   │
│   ├── chat/
│   │   └── [id]/
│   │       └── page.tsx    # Individual chat view
│   │
│   └── documents/
│       └── page.tsx        # Document management
│
├── api/
│   └── ...                 # API routes (if needed)
│
components/
├── ui/                     # shadcn components
├── chat/
│   ├── ChatInterface.tsx
│   ├── MessageList.tsx
│   ├── MessageInput.tsx
│   └── StreamingMessage.tsx
├── documents/
│   ├── DocumentUpload.tsx
│   ├── DocumentList.tsx
│   └── DocumentCard.tsx
└── layout/
    ├── Sidebar.tsx
    ├── Header.tsx
    └── AppShell.tsx

hooks/
├── useChat.ts
├── useDocuments.ts
├── useStreaming.ts
└── useAuth.ts

lib/
├── api.ts                  # API client
├── auth.ts                 # Auth utilities
└── utils.ts
```

---

## 7. Security Considerations

### Authentication
- JWT tokens with 15-minute expiry
- Refresh tokens with 7-day expiry
- HTTP-only cookies for refresh tokens
- Password hashing with bcrypt (12 rounds)

### Authorization
- Row-level security via user_id foreign keys
- Document access scoped to owner only
- Chat access verified before message operations

### Data Protection
- API keys in environment variables only
- No sensitive data in logs
- HTTPS for all communications
- CORS configured for specific origins

### Rate Limiting
- 100 requests/minute per IP
- 10 document uploads/hour per user
- 50 messages/minute per user

---

## 8. Deployment Architecture

### Frontend (Vercel)
```
Build: next build
Output: .next/
Env: Production
Features: Edge functions, ISR
```

### Backend (Railway/Render)
```
Runtime: Python 3.11
Server: Uvicorn (ASGI)
Workers: 4 (configurable)
Auto-deploy: On git push
```

### Database (Neon/Supabase)
```
Type: PostgreSQL 15
Extensions: pgvector
Backups: Daily automated
Region: US East
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://...

# AI
OPENAI_API_KEY=sk-...

# Auth
SECRET_KEY=random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# App
FRONTEND_URL=https://...
BACKEND_URL=https://...
```

---

## 9. Testing Strategy

### Backend Tests
```
tests/
├── conftest.py             # Fixtures
├── test_auth.py            # Authentication
├── test_documents.py       # Document operations
├── test_chat.py            # Chat endpoints
├── test_rag.py             # RAG pipeline
└── test_websocket.py       # Streaming
```

### Frontend Tests
```
__tests__/
├── components/
│   ├── ChatInterface.test.tsx
│   └── DocumentUpload.test.tsx
├── hooks/
│   └── useChat.test.ts
└── integration/
    └── chat-flow.test.tsx
```

### Test Coverage Targets
- Backend: 80% minimum
- Frontend: 70% minimum
- Critical paths: 100%

---

## 10. Development Milestones

### Phase 1: Foundation (Week 1)
- [ ] Database schema and migrations
- [ ] Authentication system
- [ ] Basic FastAPI structure
- [ ] Document upload endpoint

### Phase 2: RAG Core (Week 2)
- [ ] Document processing pipeline
- [ ] Chunking and embedding
- [ ] Vector search implementation
- [ ] Basic chat endpoint

### Phase 3: Frontend (Week 3)
- [ ] Next.js project setup
- [ ] Authentication UI
- [ ] Document management UI
- [ ] Chat interface

### Phase 4: Real-time (Week 4)
- [ ] WebSocket implementation
- [ ] Streaming responses
- [ ] Source citations UI
- [ ] Mobile responsiveness

### Phase 5: Polish (Week 5)
- [ ] Error handling
- [ ] Loading states
- [ ] Testing
- [ ] Documentation

---

## Appendix: Key Decisions

1. **Why LangChain over LlamaIndex?** LangChain offers more flexibility for custom RAG pipelines without enforcing specific abstractions.

2. **Why text-embedding-3-small over ada-002?** Better performance, lower cost, and sufficient quality for this use case.

3. **Why 512 token chunks?** Balances context preservation with retrieval precision. Smaller chunks lose context; larger chunks dilute relevance.

4. **Why IVFFlat index?** Good balance of query speed and recall for datasets under 1M vectors. Can upgrade to HNSW if needed.

5. **Why WebSocket over SSE?** Full-duplex communication enables future features like canceling streams or sending follow-up context.
