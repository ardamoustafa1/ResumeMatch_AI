import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from backend.main import app


async def test_generate_ws_ticket(client: AsyncClient):
    # Require auth headers
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "ValidPassword!123"},
    )
    assert login_resp.status_code == 200

    client.cookies.update(login_resp.cookies)
    resp = await client.post(
        "/api/v1/ws/ticket",
        params={"analysis_id": "test-analysis"},
    )
    assert resp.status_code == 200
    assert "ticket" in resp.json()
    ticket = resp.json()["ticket"]

    # Verify redis has the ticket
    import redis.asyncio as redis
    from backend.tasks.progress_events import REDIS_URL

    test_redis = redis.from_url(REDIS_URL)
    val = await test_redis.get(f"ws_ticket:{ticket}:test-analysis")
    assert val is not None
    assert val.decode() == "qa@example.com"
    await test_redis.aclose()


def test_websocket_missing_ticket():
    # We use TestClient for sync websocket connections
    client = TestClient(app)
    with pytest.raises(Exception) as exc_info:
        with client.websocket_connect("/api/v1/ws/analysis/test-analysis"):
            pass
    # The server closes connection due to policy violation (1008)
    # TestClient raises WebSocketDisconnect internally
    assert exc_info.type.__name__ == "WebSocketDisconnect"
    assert exc_info.value.code == 1008
