from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from backend.db.connection import get_db
from backend.main import app
from tests.conftest import ANALYSIS_ID, USER_ID

pytestmark = pytest.mark.asyncio


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
    assert response.json()["analysis_id"] == ANALYSIS_ID


async def test_post_analysis_validates_input(client: AsyncClient, sample_jd):
    response = await client.post(
        "/api/v1/analysis",
        json={"cv_text": "Too short", "jd_text": sample_jd},
    )

    assert response.status_code == 422


async def test_get_pending_analysis(client: AsyncClient):
    response = await client.get(f"/api/v1/analysis/{ANALYSIS_ID}")

    assert response.status_code == 200
    assert response.json()["status"] == "pending"


async def test_get_completed_analysis(client: AsyncClient):
    class CompletedConnection:
        async def fetchrow(self, *args, **kwargs):
            return {
                "id": ANALYSIS_ID,
                "user_id": USER_ID,
                "status": "completed",
                "result": {
                    "match_result": {
                        "score": 100,
                        "matched_skills": [],
                        "missing_skills": [],
                        "improvement_suggestions": [],
                    },
                    "outreach_messages": None,
                    "profile_improvements": None,
                    "errors": {},
                },
                "created_at": datetime.now(timezone.utc),
                "cv_text": "",
                "jd_text": "",
                "company": "",
                "recruiter_name": "",
            }

    async def override():
        yield CompletedConnection()

    app.dependency_overrides[get_db] = override
    try:
        response = await client.get(f"/api/v1/analysis/{ANALYSIS_ID}")
        assert response.status_code == 200
        assert response.json()["result"]["match_result"]["score"] == 100
    finally:
        from tests.conftest import override_get_db

        app.dependency_overrides[get_db] = override_get_db


async def test_get_analysis_rejects_wrong_owner(client: AsyncClient):
    class OtherOwnerConnection:
        async def fetchrow(self, *args, **kwargs):
            return {
                "id": ANALYSIS_ID,
                "user_id": "00000000-0000-0000-0000-000000000000",
                "status": "pending",
                "result": None,
                "created_at": datetime.now(timezone.utc),
                "cv_text": "",
                "jd_text": "",
                "company": "",
                "recruiter_name": "",
            }

    async def override():
        yield OtherOwnerConnection()

    app.dependency_overrides[get_db] = override
    try:
        response = await client.get(f"/api/v1/analysis/{ANALYSIS_ID}")
        assert response.status_code == 403
    finally:
        from tests.conftest import override_get_db

        app.dependency_overrides[get_db] = override_get_db
