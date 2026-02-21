# AI Chatbot with RAG Portfolio Project

Full-stack implementation from `docs/DESIGN.md`.

## Stack
- Frontend: Next.js 14, React 18, TypeScript, Tailwind, TanStack Query
- Backend: FastAPI, SQLAlchemy 2.x, JWT auth, WebSocket streaming
- RAG: chunking + embeddings + similarity retrieval + context-augmented generation
- DB: SQLite by default, PostgreSQL + pgvector supported via Docker

## Repository Structure
- `frontend/` Next.js app router UI (auth, documents, chat)
- `backend/` FastAPI API (`/api/v1`) with RAG pipeline
- `docs/` design and setup guides

## Implemented Features
- JWT authentication (`register`, `login`, `refresh`, `logout`)
- Document upload/list/get/delete for `pdf/txt/md`
- Chunking, embeddings, vector-style similarity retrieval
- Chat create/list/get/delete
- Message create/list + WebSocket stream endpoint
- Backend tests (auth/documents/chat/rag/websocket)
- Frontend component/hook/integration tests scaffold

## Quick Start
See `docs/SETUP.md`.
