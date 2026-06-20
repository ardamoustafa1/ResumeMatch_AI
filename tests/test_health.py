import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_alive(client: AsyncClient):
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "version": "1.0.0"}


@pytest.mark.asyncio
async def test_health_check_ready_degraded(client: AsyncClient, mocker):
    mocker.patch(
        "backend.api.v1.routes.health.async_redis_client.ping",
        side_effect=Exception("Redis down"),
    )
    mocker.patch("backend.db.connection.get_db")

    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["redis"] == "down"
