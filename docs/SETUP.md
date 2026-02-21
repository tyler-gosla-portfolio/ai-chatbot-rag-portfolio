# Setup

## 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[test]
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## 2) Frontend

```bash
cd frontend
npm install
cat > .env.local <<'ENV'
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000/api/v1
ENV
npm run dev
```

## 3) Tests

```bash
cd backend && pytest -q
cd frontend && npm test
```

## 4) Optional PostgreSQL + pgvector

```bash
cd backend
docker compose up -d
```

Set `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rag_app
```
