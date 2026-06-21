"""Tests for analysis_tasks.py - covers _process_analysis and _mark_analysis_failed."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

pytestmark = pytest.mark.asyncio


def make_mock_pool(record=None, acquired=True):
    """Create a mock db_pool with a mock connection context manager."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = record
    mock_conn.fetchval.return_value = None
    mock_conn.execute.return_value = "UPDATE 1"

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

    mock_db_pool = MagicMock()
    mock_db_pool.pool = mock_pool
    return mock_db_pool, mock_conn


async def test_process_analysis_already_completed(mocker):
    """If analysis is already completed, skip without doing anything."""
    record = {"status": "completed", "cv_text": "cv", "jd_text": "jd", "company": "Corp", "recruiter_name": "Bob", "user_id": "user-1"}
    mock_db_pool, mock_conn = make_mock_pool(record)

    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value=record)
    mock_publish = mocker.patch("backend.tasks.analysis_tasks.publish_progress_sync")

    from backend.tasks.analysis_tasks import _process_analysis
    await _process_analysis("analysis-001")

    mock_publish.assert_not_called()


async def test_process_analysis_lock_not_acquired(mocker):
    """If Redis lock cannot be acquired, raise RuntimeError."""
    record = {"status": "pending", "cv_text": "cv", "jd_text": "jd", "company": "Corp", "recruiter_name": "Bob", "user_id": "user-1"}
    mock_db_pool, mock_conn = make_mock_pool(record)

    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value=record)
    mocker.patch("backend.tasks.analysis_tasks.update_analysis_result", return_value=True)
    mocker.patch("backend.tasks.analysis_tasks.publish_progress_sync")

    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=None)  # lock NOT acquired
    mock_redis.get = AsyncMock(return_value=b"other-token")
    mock_redis.delete = AsyncMock()
    mocker.patch("backend.tasks.analysis_tasks.async_redis_client", mock_redis)

    from backend.tasks.analysis_tasks import _process_analysis
    with pytest.raises(RuntimeError, match="Lock could not be acquired"):
        await _process_analysis("analysis-001")


async def test_process_analysis_record_not_found(mocker):
    """If record doesn't exist, raise LookupError."""
    mock_db_pool, mock_conn = make_mock_pool(None)

    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value=None)

    from backend.tasks.analysis_tasks import _process_analysis
    with pytest.raises(LookupError):
        await _process_analysis("nonexistent-id")


async def test_process_analysis_no_pool(mocker):
    """If DB pool is None, raise RuntimeError."""
    mock_db_pool = MagicMock()
    mock_db_pool.pool = None
    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)

    from backend.tasks.analysis_tasks import _process_analysis
    with pytest.raises(RuntimeError, match="DB pool not initialized"):
        await _process_analysis("analysis-001")


async def test_process_analysis_success(mocker):
    """Full happy path: lock acquired, AI runs, result saved."""
    record = {
        "status": "pending",
        "cv_text": "A" * 100,
        "jd_text": "B" * 100,
        "company": "Corp",
        "recruiter_name": "Alice",
        "user_id": "user-1",
    }
    mock_db_pool, mock_conn = make_mock_pool(record)
    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value=record)
    mocker.patch("backend.tasks.analysis_tasks.update_analysis_result", return_value=True)
    mocker.patch("backend.tasks.analysis_tasks.publish_progress_sync")
    mocker.patch("backend.tasks.analysis_tasks.get_telegram_config", return_value=None)

    mock_match = MagicMock()
    mock_outreach = MagicMock()
    mock_profile = MagicMock()

    mocker.patch("backend.tasks.analysis_tasks.analyze_cv_jd_match", return_value=mock_match)
    mocker.patch("backend.tasks.analysis_tasks.generate_outreach_messages", return_value=mock_outreach)
    mocker.patch("backend.tasks.analysis_tasks.generate_profile_improvements", return_value=mock_profile)

    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=True)  # lock acquired
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.delete = AsyncMock()
    mocker.patch("backend.tasks.analysis_tasks.async_redis_client", mock_redis)

    from backend.tasks.analysis_tasks import _process_analysis
    await _process_analysis("analysis-001")

    mock_redis.set.assert_called_once()


async def test_process_analysis_outreach_fails_partial(mocker):
    """If outreach generation fails, result is partial_completed."""
    record = {
        "status": "pending",
        "cv_text": "A" * 100,
        "jd_text": "B" * 100,
        "company": "Corp",
        "recruiter_name": "Alice",
        "user_id": "user-1",
    }
    mock_db_pool, mock_conn = make_mock_pool(record)
    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value=record)
    mocker.patch("backend.tasks.analysis_tasks.update_analysis_result", return_value=True)
    mock_publish = mocker.patch("backend.tasks.analysis_tasks.publish_progress_sync")
    mocker.patch("backend.tasks.analysis_tasks.get_telegram_config", return_value=None)

    mocker.patch("backend.tasks.analysis_tasks.analyze_cv_jd_match", return_value=MagicMock())
    mocker.patch("backend.tasks.analysis_tasks.generate_outreach_messages", side_effect=Exception("AI Error"))
    mocker.patch("backend.tasks.analysis_tasks.generate_profile_improvements", return_value=MagicMock())

    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.delete = AsyncMock()
    mocker.patch("backend.tasks.analysis_tasks.async_redis_client", mock_redis)

    from backend.tasks.analysis_tasks import _process_analysis
    await _process_analysis("analysis-001")

    # Should have published partial_completed
    calls = [str(c) for c in mock_publish.call_args_list]
    assert any("partial_completed" in c for c in calls)


async def test_mark_analysis_failed_no_pool(mocker):
    """_mark_analysis_failed should return gracefully if pool is None."""
    mock_db_pool = MagicMock()
    mock_db_pool.pool = None
    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)

    from backend.tasks.analysis_tasks import _mark_analysis_failed
    await _mark_analysis_failed("analysis-001", Exception("test"))


async def test_mark_analysis_failed_with_pool(mocker):
    """_mark_analysis_failed should mark the record as failed."""
    record = {"status": "pending", "user_id": "user-1"}
    mock_db_pool, mock_conn = make_mock_pool(record)
    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value=record)
    mock_update = mocker.patch("backend.tasks.analysis_tasks.update_analysis_result", return_value=True)
    mock_publish = mocker.patch("backend.tasks.analysis_tasks.publish_progress_sync")
    mocker.patch("backend.tasks.analysis_tasks.get_telegram_config", return_value=None)
    mocker.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": ""})

    from backend.tasks.analysis_tasks import _mark_analysis_failed
    await _mark_analysis_failed("analysis-001", Exception("test error"))

    mock_update.assert_called_once_with(
        mock_conn,
        "analysis-001",
        "failed",
        {"error": "Analysis could not be completed after multiple attempts."},
    )
    mock_publish.assert_called_once()


async def test_mark_analysis_failed_already_completed(mocker):
    """_mark_analysis_failed should not overwrite already-completed records."""
    record = {"status": "completed", "user_id": "user-1"}
    mock_db_pool, mock_conn = make_mock_pool(record)
    mocker.patch("backend.tasks.analysis_tasks.db_pool", mock_db_pool)
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value=record)
    mock_update = mocker.patch("backend.tasks.analysis_tasks.update_analysis_result")

    from backend.tasks.analysis_tasks import _mark_analysis_failed
    await _mark_analysis_failed("analysis-001", Exception("test"))

    mock_update.assert_not_called()
