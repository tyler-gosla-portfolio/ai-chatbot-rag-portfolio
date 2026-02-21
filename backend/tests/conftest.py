import os
import tempfile
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.db.session import get_db
from app.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


@pytest.fixture
def test_db_url():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        yield f"sqlite+aiosqlite:///{tmp.name}"


@pytest.fixture
async def app(test_db_url):
    os.environ["DATABASE_URL"] = test_db_url
    os.environ["SECRET_KEY"] = "test-secret"

    engine = create_async_engine(test_db_url, future=True)
    TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db] = override_get_db
    yield application
    await engine.dispose()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(client):
    payload = {"email": "test@example.com", "password": "password123"}
    response = await client.post("/api/v1/auth/register", json=payload)
    token = response.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
