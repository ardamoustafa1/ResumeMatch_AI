import pytest
from httpx import AsyncClient
from backend.main import app

pytestmark = pytest.mark.asyncio



async def test_websocket_ticket_generation(client: AsyncClient, mocker):
    mock_set = mocker.patch("backend.api.v1.websocket.async_redis_client.set", new_callable=mocker.AsyncMock, return_value=True)
    
    response = await client.post(
        "/api/v1/ws/ticket?analysis_id=123",
        headers={"Authorization": "Bearer fake_token"}
    )
    
    assert response.status_code == 200
    assert "ticket" in response.json()
    mock_set.assert_called_once()

async def test_websocket_connection_requires_ticket(mocker):
    from backend.api.v1.websocket import _authorize
    from fastapi import WebSocket
    
    mock_ws = mocker.MagicMock(spec=WebSocket)
    mock_ws.headers = {}
    mock_ws.query_params = {"ticket": "test-ticket"}
    
    # Mock redis to return None (invalid ticket)
    mocker.patch("backend.api.v1.websocket.async_redis_client.get", new_callable=mocker.AsyncMock, return_value=None)
    
    is_valid = await _authorize(mock_ws, "analysis-id")
    assert is_valid is False
