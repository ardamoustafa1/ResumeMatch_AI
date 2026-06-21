import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket
from httpx import AsyncClient


async def test_websocket_ticket_generation(client: AsyncClient, mocker):
    mock_set = mocker.patch(
        "backend.api.v1.websocket.async_redis_client.set",
        new_callable=mocker.AsyncMock,
        return_value=True,
    )

    response = await client.post(
        "/api/v1/ws/ticket?analysis_id=123",
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    assert "ticket" in response.json()
    mock_set.assert_called_once()


async def test_websocket_connection_requires_ticket(mocker):
    from backend.api.v1.websocket import _authorize

    mock_ws = mocker.MagicMock(spec=WebSocket)
    mock_ws.headers = {}
    mock_ws.query_params = {"ticket": "test-ticket"}

    mocker.patch(
        "backend.api.v1.websocket.async_redis_client.get",
        new_callable=mocker.AsyncMock,
        return_value=None,
    )

    is_valid = await _authorize(mock_ws, "analysis-id")
    assert is_valid is False


# ── New: ConnectionManager unit tests ────────────────────────────────────────


async def test_connection_manager_connect_and_disconnect():
    from backend.core.websocket_manager import ConnectionManager

    manager = ConnectionManager()
    mock_ws = MagicMock(spec=WebSocket)
    mock_ws.accept = AsyncMock()

    # Patch the redis task so it doesn't actually run
    with patch.object(manager, "_listen_to_redis", new=AsyncMock()):
        with patch("asyncio.create_task") as mock_create_task:
            mock_task = MagicMock()

            def capture_task(coroutine):
                coroutine.close()
                return mock_task

            mock_create_task.side_effect = capture_task

            await manager.connect(mock_ws, "analysis-001")
            assert "analysis-001" in manager.active_connections
            assert mock_ws in manager.active_connections["analysis-001"]
            mock_ws.accept.assert_awaited_once()

    # Disconnect
    manager.disconnect(mock_ws, "analysis-001")
    assert "analysis-001" not in manager.active_connections


async def test_connection_manager_disconnect_cancels_redis_task():
    from backend.core.websocket_manager import ConnectionManager

    manager = ConnectionManager()
    mock_ws = MagicMock(spec=WebSocket)
    mock_ws.accept = AsyncMock()
    mock_task = MagicMock()

    def capture_task(coroutine):
        coroutine.close()
        return mock_task

    with patch("asyncio.create_task", side_effect=capture_task):
        with patch.object(manager, "_listen_to_redis", new=AsyncMock()):
            await manager.connect(mock_ws, "analysis-002")

    manager.disconnect(mock_ws, "analysis-002")
    mock_task.cancel.assert_called_once()


async def test_listen_to_redis_broadcasts_and_stops_on_done():
    from backend.core.websocket_manager import ConnectionManager

    manager = ConnectionManager()
    mock_ws = MagicMock(spec=WebSocket)
    mock_ws.send_text = AsyncMock()

    # Pre-populate a connection
    manager.active_connections["analysis-003"] = {mock_ws}

    done_message = json.dumps({"step": "done", "result": "ok"}).encode()

    fake_messages = [
        {"type": "subscribe", "data": 1},
        {"type": "message", "data": done_message},
    ]

    mock_pubsub = MagicMock()
    mock_pubsub.subscribe = AsyncMock()
    mock_pubsub.unsubscribe = AsyncMock()
    mock_pubsub.listen = lambda: aiter_from_list(fake_messages)

    mock_redis = MagicMock()
    mock_redis.pubsub.return_value = mock_pubsub

    with patch("backend.core.websocket_manager.async_redis_client", mock_redis):
        await manager._listen_to_redis("analysis-003")

    # Should have sent the done message
    mock_ws.send_text.assert_awaited_once_with(done_message.decode())
    mock_pubsub.unsubscribe.assert_awaited_once()


async def test_listen_to_redis_handles_disconnected_ws():
    from backend.core.websocket_manager import ConnectionManager

    manager = ConnectionManager()
    broken_ws = MagicMock(spec=WebSocket)
    broken_ws.send_text = AsyncMock()
    broken_ws.send_text.side_effect = RuntimeError("connection broken")

    manager.active_connections["analysis-004"] = {broken_ws}

    error_message = json.dumps({"step": "progress"}).encode()

    fake_messages = [
        {"type": "message", "data": error_message},
        # After disconnect, stop because active_connections no longer has analysis-004
    ]

    mock_pubsub = MagicMock()
    mock_pubsub.subscribe = AsyncMock()
    mock_pubsub.unsubscribe = AsyncMock()
    mock_pubsub.listen = lambda: aiter_from_list(fake_messages)

    mock_redis = MagicMock()
    mock_redis.pubsub.return_value = mock_pubsub

    with patch("backend.core.websocket_manager.async_redis_client", mock_redis):
        await manager._listen_to_redis("analysis-004")

    # The broken ws should have been disconnected
    assert "analysis-004" not in manager.active_connections
    mock_pubsub.unsubscribe.assert_awaited_once()


# ── Helper: async iterator from list ────────────────────────────────────────


async def aiter_from_list(items):
    for item in items:
        yield item
