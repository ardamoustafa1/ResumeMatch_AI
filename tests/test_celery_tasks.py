import pytest
from backend.tasks.analysis_tasks import _process_analysis
from backend.models.schemas import MatchResult

pytestmark = pytest.mark.asyncio

async def test_task_updates_status_to_processing(mocker):
    """Ensure the worker transitions the DB record to processing before AI calls."""
    # Arrange
    mock_update = mocker.patch("backend.tasks.analysis_tasks.update_analysis_result")
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value={
        "cv_text": "cv", "jd_text": "jd", "company": None, "recruiter_name": None
    })
    # Stub out AI services
    mocker.patch("backend.services.ai_engine.analyze_cv_jd_match", return_value=MatchResult(
        score=100, matched_skills=[], missing_skills=[], improvement_suggestions=[]
    ))
    mocker.patch("backend.services.ai_engine.generate_outreach_messages", return_value=None)
    mocker.patch("backend.services.ai_engine.generate_profile_improvements", return_value=None)
    
    # Act
    await _process_analysis("1234")

    # Assert
    # Check that update_analysis_result was called with 'processing'
    mock_update.assert_any_call(mocker.ANY, "1234", "processing")

async def test_task_updates_status_to_completed(mocker):
    """Ensure the worker transitions to completed and stores results upon success."""
    # Arrange
    mock_update = mocker.patch("backend.tasks.analysis_tasks.update_analysis_result")
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value={
        "cv_text": "cv", "jd_text": "jd", "company": None, "recruiter_name": None
    })
    mocker.patch("backend.services.ai_engine.analyze_cv_jd_match", return_value=MatchResult(
        score=100, matched_skills=[], missing_skills=[], improvement_suggestions=[]
    ))
    mocker.patch("backend.services.ai_engine.generate_outreach_messages", return_value=None)
    mocker.patch("backend.services.ai_engine.generate_profile_improvements", return_value=None)
    
    # Act
    await _process_analysis("1234")

    # Assert
    # The final DB call should be completed
    assert mock_update.call_args[0][2] == "completed"

async def test_task_updates_status_to_failed_on_error(mocker):
    """Ensure uncaught exceptions trigger the failure transition."""
    # Arrange
    mock_update = mocker.patch("backend.tasks.analysis_tasks.update_analysis_result")
    # Force DB fetch to explode
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", side_effect=Exception("DB Error"))
    
    # Act & Assert
    with pytest.raises(Exception):
        await _process_analysis("1234")

    # Ensure the failure payload was caught and stored
    mock_update.assert_any_call(mocker.ANY, "1234", "failed", {"error": "DB Error"})

async def test_task_sends_telegram_on_completion(mocker):
    """Verify that the Telegram notification hook logs/triggers on success."""
    # Arrange
    mocker.patch("backend.tasks.analysis_tasks.update_analysis_result")
    mocker.patch("backend.tasks.analysis_tasks.get_analysis", return_value={
        "cv_text": "cv", "jd_text": "jd", "company": None, "recruiter_name": None
    })
    mocker.patch("backend.services.ai_engine.analyze_cv_jd_match", return_value=MatchResult(
        score=100, matched_skills=[], missing_skills=[], improvement_suggestions=[]
    ))
    mocker.patch("backend.services.ai_engine.generate_outreach_messages", return_value=None)
    mocker.patch("backend.services.ai_engine.generate_profile_improvements", return_value=None)
    
    mock_logger = mocker.patch("backend.tasks.analysis_tasks.logger.info")
    
    # Act
    await _process_analysis("1234")

    # Assert
    # We haven't built the full telegram hook yet, but we assert the code path reached the completion log
    mock_logger.assert_any_call("Analysis 1234 completed. Sending Telegram notification...")
