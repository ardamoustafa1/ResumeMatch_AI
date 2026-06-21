"""Tests for db/queries.py."""

from unittest.mock import AsyncMock
from backend.db.queries import (
    create_analysis,
    get_analysis,
    update_analysis_result,
    get_user_analyses,
    get_telegram_config,
)


def make_conn():
    """Return a mock asyncpg-like connection."""
    conn = AsyncMock()
    return conn


async def test_create_analysis():
    conn = make_conn()
    import uuid

    fake_id = uuid.uuid4()
    conn.fetchval.return_value = fake_id

    result = await create_analysis(conn, "user-1", "cv", "jd", "Company", "Alice")

    conn.fetchval.assert_called_once()
    assert result == str(fake_id)


async def test_get_analysis_found():
    conn = make_conn()
    import uuid

    user_id = uuid.uuid4()
    analysis_id = uuid.uuid4()
    row = {
        "id": analysis_id,
        "user_id": user_id,
        "cv_text": "cv",
        "jd_text": "jd",
        "company": "Corp",
        "recruiter_name": "Bob",
        "status": "completed",
        "result": '{"score": 90}',
        "created_at": "2025-01-01",
    }
    conn.fetchrow.return_value = row

    record = await get_analysis(conn, str(analysis_id))

    assert record is not None
    assert record["id"] == str(analysis_id)
    assert record["user_id"] == str(user_id)
    assert record["result"] == {"score": 90}


async def test_get_analysis_not_found():
    conn = make_conn()
    conn.fetchrow.return_value = None

    result = await get_analysis(conn, "nonexistent-id")
    assert result is None


async def test_get_analysis_result_already_dict():
    """If result is already a dict (asyncpg jsonb), don't double-parse."""
    conn = make_conn()
    import uuid

    user_id = uuid.uuid4()
    analysis_id = uuid.uuid4()
    row = {
        "id": analysis_id,
        "user_id": user_id,
        "cv_text": "cv",
        "jd_text": "jd",
        "company": "Corp",
        "recruiter_name": "Bob",
        "status": "completed",
        "result": {"score": 90},  # already a dict
        "created_at": "2025-01-01",
    }
    conn.fetchrow.return_value = row

    record = await get_analysis(conn, str(analysis_id))
    assert record["result"] == {"score": 90}


async def test_update_analysis_result_success():
    conn = make_conn()
    conn.execute.return_value = "UPDATE 1"

    ok = await update_analysis_result(conn, "analysis-1", "completed", {"score": 85})

    conn.execute.assert_called_once()
    assert ok is True


async def test_update_analysis_result_no_rows():
    conn = make_conn()
    conn.execute.return_value = "UPDATE 0"

    ok = await update_analysis_result(conn, "analysis-1", "failed", None)
    assert ok is False


async def test_update_analysis_result_no_result():
    conn = make_conn()
    conn.execute.return_value = "UPDATE 1"

    ok = await update_analysis_result(conn, "analysis-1", "failed", None)
    assert ok is True


async def test_get_user_analyses():
    conn = make_conn()
    import uuid

    uid = uuid.uuid4()
    aid = uuid.uuid4()
    rows = [
        {
            "id": aid,
            "user_id": uid,
            "company": "Corp",
            "recruiter_name": "Bob",
            "status": "completed",
            "created_at": "2025-01-01",
        }
    ]
    conn.fetch.return_value = rows

    results = await get_user_analyses(conn, str(uid), limit=10, offset=0)

    conn.fetch.assert_called_once()
    assert len(results) == 1
    assert results[0]["id"] == str(aid)
    assert results[0]["user_id"] == str(uid)


async def test_get_user_analyses_empty():
    conn = make_conn()
    conn.fetch.return_value = []

    results = await get_user_analyses(conn, "user-1")
    assert results == []


async def test_get_telegram_config_found():
    conn = make_conn()
    conn.fetchrow.return_value = {"chat_id": "chat123", "is_active": True}

    result = await get_telegram_config(conn, "user-1")
    assert result == {"chat_id": "chat123", "is_active": True}


async def test_get_telegram_config_not_found():
    conn = make_conn()
    conn.fetchrow.return_value = None

    result = await get_telegram_config(conn, "user-1")
    assert result is None
