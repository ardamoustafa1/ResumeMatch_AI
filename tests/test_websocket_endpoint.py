import asyncio
import pytest
from httpx import AsyncClient
from backend.db.connection import db_pool
from tests.conftest import USER_ID
from fastapi.testclient import TestClient
from backend.main import app
from backend.tasks.progress_events import async_redis_client

pytestmark = pytest.mark.asyncio


async def test_generate_ws_ticket(client: AsyncClient):
    # Require auth headers
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "ValidPassword!123"},
    )
    assert login_resp.status_code == 200

    resp = await client.post(
        "/api/v1/ws/ticket",
        params={"analysis_id": "test-analysis"},
        cookies=login_resp.cookies,
    )
    assert resp.status_code == 200
    assert "ticket" in resp.json()
    ticket = resp.json()["ticket"]

    # Verify redis has the ticket
    val = await async_redis_client.get(f"ws_ticket:{ticket}:test-analysis")
    assert val is not None
    assert val.decode() == "qa@example.com"


def test_websocket_missing_ticket():
    # We use TestClient for sync websocket connections
    client = TestClient(app)
    with pytest.raises(Exception) as exc_info:
        with client.websocket_connect("/api/v1/ws/analysis/test-analysis") as ws:
            pass
    # The server closes connection due to policy violation (1008)
    # TestClient raises WebSocketDisconnect internally
    assert exc_info.type.__name__ == "WebSocketDisconnect"
    assert exc_info.value.code == 1008
