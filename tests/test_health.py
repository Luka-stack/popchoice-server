from collections.abc import AsyncIterator
from typing import Any

from httpx import AsyncClient

from app.db.session import get_session
from app.main import app


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_returns_503_when_db_is_down(client: AsyncClient) -> None:
    class BrokenSession:
        async def execute(self, *_: Any) -> None:
            raise ConnectionError("db down")

    async def broken_session() -> AsyncIterator[BrokenSession]:
        yield BrokenSession()

    app.dependency_overrides[get_session] = broken_session
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 503
