from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.models.schemas import (
    MatchResult,
    OutreachMessages,
    ProfileImprovements,
)
from backend.tasks.analysis_tasks import _process_analysis
from tests.conftest import ANALYSIS_ID, USER_ID

pytestmark = pytest.mark.asyncio


class FakeConnection:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def analysis_record(status="pending"):
    return {
        "id": ANALYSIS_ID,
        "user_id": USER_ID,
        "cv_text": "Python FastAPI PostgreSQL Redis " * 8,
        "jd_text": "Senior Python backend role " * 8,
        "company": "TestCorp",
        "recruiter_name": "Alice",
        "status": status,
        "result": None,
    }


@pytest.fixture
def task_mocks(mocker):
    pool_mock = MagicMock()
    acquire_ctx = AsyncMock()
    acquire_ctx.__aenter__.return_value = FakeConnection()
    pool_mock.acquire.return_value = acquire_ctx
    mocker.patch("backend.tasks.analysis_tasks.db_pool.pool", pool_mock)
    mocker.patch(
        "backend.tasks.analysis_tasks.publish_progress_sync",
        return_value=None,
    )
    mocker.patch(
        "backend.tasks.analysis_tasks.async_redis_client.set",
        new_callable=AsyncMock,
        return_value=True,
    )
    mocker.patch(
        "backend.tasks.analysis_tasks.async_redis_client.delete",
        new_callable=AsyncMock,
        return_value=True,
    )
    update = mocker.patch("backend.tasks.analysis_tasks.update_analysis_result")
    mocker.patch(
        "backend.tasks.analysis_tasks.get_analysis",
        return_value=analysis_record(),
    )
    mocker.patch(
        "backend.tasks.analysis_tasks.get_telegram_config",
        return_value=None,
    )
    mocker.patch(
        "backend.tasks.analysis_tasks.analyze_cv_jd_match",
        return_value=MatchResult(
            score=90,
            matched_skills=["Python"],
            missing_skills=[],
            improvement_suggestions=[],
        ),
    )
    mocker.patch(
        "backend.tasks.analysis_tasks.generate_outreach_messages",
        return_value=OutreachMessages(
            dm_first_contact="Hello",
            dm_follow_up="Following up",
            connection_note="Let's connect",
        ),
    )
    mocker.patch(
        "backend.tasks.analysis_tasks.generate_profile_improvements",
        return_value=ProfileImprovements(
            headline_before="Engineer",
            headline_after="Senior Python Engineer",
            about_section="I build reliable systems.",
        ),
    )
    return update


async def test_task_persists_completed_result(task_mocks):
    await _process_analysis(ANALYSIS_ID)

    statuses = [call.args[2] for call in task_mocks.call_args_list]
    assert statuses == ["processing", "completed"]


async def test_task_marks_partial_result_when_optional_stage_fails(
    mocker,
    task_mocks,
):
    mocker.patch(
        "backend.tasks.analysis_tasks.generate_outreach_messages",
        side_effect=RuntimeError("provider failed"),
    )

    await _process_analysis(ANALYSIS_ID)

    final_call = task_mocks.call_args_list[-1]
    assert final_call.args[2] == "partial_completed"
    assert "outreach_messages" in final_call.args[3]["errors"]


async def test_task_is_idempotent_for_completed_record(mocker, task_mocks):
    mocker.patch(
        "backend.tasks.analysis_tasks.get_analysis",
        return_value=analysis_record("completed"),
    )

    await _process_analysis(ANALYSIS_ID)

    task_mocks.assert_not_called()


async def test_match_failure_propagates(mocker, task_mocks):
    mocker.patch(
        "backend.tasks.analysis_tasks.analyze_cv_jd_match",
        side_effect=RuntimeError("provider failed"),
    )

    with pytest.raises(RuntimeError):
        await _process_analysis(ANALYSIS_ID)

    assert task_mocks.call_args_list[-1].args[2] == "processing"


async def test_purge_old_data_task(mocker):
    from backend.tasks.analysis_tasks import purge_old_data_task
    
    # Mock db_pool to avoid actual connection
    mocker.patch("backend.tasks.analysis_tasks.db_pool.connect", new_callable=mocker.AsyncMock)
    
    pool_mock = mocker.MagicMock()
    acquire_ctx = mocker.AsyncMock()
    
    class FakeConn:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def execute(self, *args, **kwargs):
            return "DELETE 5"
            
    acquire_ctx.__aenter__.return_value = FakeConn()
    pool_mock.acquire.return_value = acquire_ctx
    
    mocker.patch("backend.tasks.analysis_tasks.db_pool.pool", pool_mock)
    
    # Execute the synchronous celery task, which runs the async _purge internally
    # But since it calls asyncio.run(), we must be careful with event loops.
    captured_coro = None
    def mock_run(coro):
        nonlocal captured_coro
        captured_coro = coro
        
    mocker.patch("backend.tasks.analysis_tasks._run", side_effect=mock_run)
    
    # Run the synchronous function which will pass the coroutine to our mock
    if hasattr(purge_old_data_task, "__wrapped__"):
        purge_old_data_task.__wrapped__()
    else:
        purge_old_data_task()
        
    # Now await the captured coroutine inside the pytest-asyncio event loop
    assert captured_coro is not None
    await captured_coro

