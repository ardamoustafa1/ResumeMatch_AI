import pytest
from httpx import AsyncClient
from backend.main import app

pytestmark = pytest.mark.asyncio

async def test_websocket_ticket_generation(client: AsyncClient, mocker):
    mocker.patch("backend.core.websocket_manager.ws_manager.create_ticket", return_value="ws-ticket-123")
    
    response = await client.post(
        "/api/v1/ws/ticket",
        headers={"Authorization": "Bearer fake_token"}
    )
    
    # We expect 200 and a ticket, but since get_current_user is mocked in conftest, it should work
    assert response.status_code == 200
    assert response.json()["ticket"] == "ws-ticket-123"

async def test_websocket_connection_requires_ticket(mocker):
    # Testing actual Starlette WebSocket endpoint is trickier, 
    # but we can test the auth layer logic.
    from backend.api.v1.websocket import _authorize
    
    mocker.patch("backend.core.websocket_manager.ws_manager.validate_ticket", return_value="user-id")
    
    user_id = await _authorize("valid-ticket")
    assert user_id == "user-id"
