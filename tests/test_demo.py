from httpx import AsyncClient


async def test_demo_endpoint_returns_instant_mock(client: AsyncClient):
    # Unauthenticated post request
    response = await client.post("/api/v1/analysis/demo")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "React" in data["result"]["match_result"]["matched_skills"]
    assert data["result"]["match_result"]["score"] == 92
