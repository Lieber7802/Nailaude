import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{(tmp_path / 'agenthub-test.db').as_posix()}")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def create_schema():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_schema())

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)
    yield test_client
    test_client.close()

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


@pytest.fixture
def create_agent(client):
    def _create_agent(platform_id="mock", name=None):
        response = client.post(
            "/api/v1/agents",
            json={
                "name": name or f"测试Agent-{uuid.uuid4()}",
                "avatar": "T",
                "description": "测试用 Agent",
                "capabilities": ["测试"],
                "systemInstruction": "你是测试用 Agent。",
                "platformId": platform_id,
            },
        )
        assert response.status_code == 200
        return response.json()["data"]

    return _create_agent
