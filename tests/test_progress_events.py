"""Tests for progress_events module."""

import json
from unittest.mock import AsyncMock
from backend.tasks.progress_events import (
    _event_name,
    _message,
    publish_progress_sync,
    publish_progress,
    STEP_MESSAGES,
)


def test_event_name_completed():
    assert _event_name("completed") == "completed"
    assert _event_name("done") == "completed"
    assert _event_name("partial_completed") == "partial_completed"


def test_event_name_failed():
    assert _event_name("failed") == "failed"


def test_event_name_progress():
    assert _event_name("validating") == "progress"
    assert _event_name("analyzing_match") == "progress"
    assert _event_name("generating_messages") == "progress"


def test_message_structure():
    msg = _message("analysis-001", "validating", 10, {"key": "value"})
    assert msg["analysis_id"] == "analysis-001"
    assert msg["event"] == "progress"
    assert msg["step"] == "validating"
    assert msg["progress"] == 10
    assert msg["message"] == STEP_MESSAGES["validating"]
    assert msg["data"] == {"key": "value"}


def test_message_empty_data():
    msg = _message("analysis-001", "done", 100, None)
    assert msg["data"] == {}
    assert msg["event"] == "completed"


def test_message_unknown_step():
    msg = _message("analysis-001", "custom_step", 50, None)
    assert msg["message"] == "Custom Step"
    assert msg["event"] == "progress"


def test_publish_progress_sync(mocker):
    mock_publish = mocker.patch(
        "backend.tasks.progress_events.sync_redis_client.publish"
    )

    publish_progress_sync("analysis-001", "validating", 10, {"result": "ok"})

    mock_publish.assert_called_once()
    call_args = mock_publish.call_args[0]
    assert call_args[0] == "analysis_progress:analysis-001"
    payload = json.loads(call_args[1])
    assert payload["step"] == "validating"
    assert payload["progress"] == 10


async def test_publish_progress(mocker):
    mock_publish = AsyncMock()
    mocker.patch(
        "backend.tasks.progress_events.async_redis_client.publish", mock_publish
    )

    await publish_progress("analysis-002", "done", 100, {"final": True})

    mock_publish.assert_called_once()
    call_args = mock_publish.call_args[0]
    assert call_args[0] == "analysis_progress:analysis-002"
    payload = json.loads(call_args[1])
    assert payload["step"] == "done"
    assert payload["event"] == "completed"
    assert payload["data"]["final"] is True
