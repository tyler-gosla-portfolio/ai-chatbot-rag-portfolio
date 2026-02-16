# PROJECT 1: AI Chatbot with RAG
## Design Brief for Claude Code

### Objective
Build a production-ready AI chatbot with Retrieval-Augmented Generation (RAG) that demonstrates full-stack AI development skills.

### Target Job Matches
- Upwork: "Full-stack AI Developer" ($5,000 fixed)
- Wellfound: "Software Development Engineer, AI" ($105k-$140k)
- Fiverr: AI chatbot gigs ($90-$300)

### Tech Stack
- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** Python, FastAPI, Pydantic
- **Database:** PostgreSQL + pgvector extension
- **AI:** OpenAI API (embeddings + chat), text-embedding-3-small
- **Deployment:** Vercel (frontend), Railway (backend + DB)

### Core Features
1. **Document Upload**
   - Support PDF, TXT, MD files
   - File size limit: 10MB
   - Drag-and-drop interface

2. **RAG Pipeline**
   - Chunk documents (semantic chunking)
   - Generate embeddings (OpenAI)
   - Store in pgvector
   - Retrieve relevant chunks
   - Generate contextual responses

3. **Chat Interface**
   - Real-time streaming responses
   - Message history persistence
   - Context-aware (references uploaded docs)
   - Copy, regenerate, delete messages

4. **Authentication**
   - JWT-based auth
   - Protected routes
   - Session management

### Database Schema
```sql
-- Users
users (id, email, password_hash, created_at)

-- Documents
documents (id, user_id, filename, file_path, content_type, status, created_at)

-- Document Chunks (for RAG)
chunks (id, document_id, content, embedding vector(1536), metadata)

-- Chat Sessions
chats (id, user_id, title, created_at)

-- Messages
messages (id, chat_id, role, content, created_at)
```

### API Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - Logout
- `POST /documents/upload` - Upload document
- `GET /documents` - List user documents
- `DELETE /documents/:id` - Delete document
- `POST /chat` - Create new chat
- `GET /chats` - List chats
- `POST /chat/:id/message` - Send message (streaming)
- `GET /chat/:id/messages` - Get message history

### Design Document Structure
Create `docs/DESIGN.md` with:
1. System Architecture (diagram)
2. Technology Choices (with rationale)
3. Database Schema (SQL + explanations)
4. API Design (OpenAPI-style spec)
5. RAG Pipeline Deep Dive
6. Frontend Component Hierarchy
7. Security Considerations
8. Deployment Architecture
9. Testing Strategy
10. Development Milestones

### Success Criteria
- [ ] Clean, documented architecture
- [ ] Scalable design decisions
- [ ] Security best practices
- [ ] Clear implementation path
- [ ] 2-hour timebox

### Output
Save complete design to:
`~/portfolio-projects/ai-chatbot-rag-portfolio/docs/DESIGN.md`
