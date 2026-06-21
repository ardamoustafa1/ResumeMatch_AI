from httpx import AsyncClient


async def test_post_analysis_returns_job_id(client: AsyncClient, sample_cv, sample_jd):
    response = await client.post(
        "/api/v1/analysis",
        json={
            "cv_text": sample_cv,
            "jd_text": sample_jd,
            "company": "TestCorp",
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert "analysis_id" in data
    # Test that the returned ID is a valid UUID
    import uuid

    assert uuid.UUID(data["analysis_id"])


async def test_post_analysis_validates_input(client: AsyncClient, sample_jd):
    response = await client.post(
        "/api/v1/analysis",
        json={"cv_text": "Too short", "jd_text": sample_jd},
    )

    assert response.status_code == 422


async def test_get_pending_analysis(client: AsyncClient, sample_cv, sample_jd):
    # Create analysis first
    post_res = await client.post(
        "/api/v1/analysis",
        json={"cv_text": sample_cv, "jd_text": sample_jd, "company": "TestCorp"},
    )
    analysis_id = post_res.json()["analysis_id"]

    response = await client.get(f"/api/v1/analysis/{analysis_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"


async def test_get_completed_analysis(client: AsyncClient, sample_cv, sample_jd):
    # Create analysis first
    post_res = await client.post(
        "/api/v1/analysis",
        json={"cv_text": sample_cv, "jd_text": sample_jd, "company": "TestCorp"},
    )
    analysis_id = post_res.json()["analysis_id"]

    # Update analysis to completed in DB
    from backend.db.connection import db_pool
    import json

    mock_result = {
        "match_result": {
            "score": 100,
            "matched_skills": [],
            "missing_skills": [],
            "improvement_suggestions": [],
        },
        "outreach_messages": None,
        "profile_improvements": None,
        "errors": {},
    }
    async with db_pool.pool.acquire() as conn:
        await conn.execute(
            "UPDATE analyses SET status = 'completed', result = $2 WHERE id = $1",
            analysis_id,
            json.dumps(mock_result),
        )

    response = await client.get(f"/api/v1/analysis/{analysis_id}")
    assert response.status_code == 200
    assert response.json()["result"]["match_result"]["score"] == 100


async def test_get_analysis_rejects_wrong_owner(
    client: AsyncClient, sample_cv, sample_jd
):
    # Create analysis first
    post_res = await client.post(
        "/api/v1/analysis",
        json={"cv_text": sample_cv, "jd_text": sample_jd, "company": "TestCorp"},
    )
    analysis_id = post_res.json()["analysis_id"]

    # Change owner in DB
    from backend.db.connection import db_pool
    import uuid

    wrong_user_id = str(uuid.uuid4())
    async with db_pool.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (id, email, hashed_password) VALUES ($1, $2, 'hash')",
            wrong_user_id,
            "wrong@test.com",
        )
        await conn.execute(
            "UPDATE analyses SET user_id = $1 WHERE id = $2", wrong_user_id, analysis_id
        )

    response = await client.get(f"/api/v1/analysis/{analysis_id}")
    assert response.status_code == 403
