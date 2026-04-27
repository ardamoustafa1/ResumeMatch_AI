import pytest
import json
from backend.services.ai_engine import (
    analyze_cv_jd_match, 
    _generate_json, 
    OpenAIError, 
    MatchResult
)

# Tell pytest these tests are asynchronous
pytestmark = pytest.mark.asyncio

async def test_match_score_returns_valid_range(mocker, sample_cv, sample_jd):
    """Ensure the match score correctly unpacks into the Pydantic schema and bounds."""
    # Arrange: Mock the raw JSON string OpenAI returns
    mock_response = {
        "score": 85,
        "matched_skills": ["Python"],
        "missing_skills": ["Java"],
        "improvement_suggestions": ["Add more Java"]
    }
    mocker.patch("backend.services.ai_engine._call_openai", return_value=json.dumps(mock_response))

    # Act: Trigger the AI wrapper
    result = await analyze_cv_jd_match(sample_cv, sample_jd)

    # Assert: Validate Pydantic schema constraints
    assert isinstance(result, MatchResult)
    assert 0 <= result.score <= 100
    assert result.score == 85

async def test_missing_skills_detected_correctly(mocker, sample_cv, sample_jd):
    """Ensure arrays are populated correctly."""
    # Arrange
    mock_response = {
        "score": 50,
        "matched_skills": [],
        "missing_skills": ["Docker", "Kubernetes"],
        "improvement_suggestions": []
    }
    mocker.patch("backend.services.ai_engine._call_openai", return_value=json.dumps(mock_response))

    # Act
    result = await analyze_cv_jd_match(sample_cv, sample_jd)

    # Assert
    assert "Docker" in result.missing_skills
    assert len(result.missing_skills) == 2

async def test_openai_fallback_to_ollama_on_error(mocker, sample_cv, sample_jd):
    """Ensure high availability by testing the local Ollama fallback sequence."""
    # Arrange
    # OpenAI fails immediately
    mocker.patch("backend.services.ai_engine._call_openai", side_effect=OpenAIError("API Down"))
    # Ollama succeeds
    mock_ollama = mocker.patch(
        "backend.services.ai_engine._call_ollama", 
        return_value='{"score": 90, "matched_skills": [], "missing_skills": [], "improvement_suggestions": []}'
    )

    # Act
    result = await analyze_cv_jd_match(sample_cv, sample_jd)

    # Assert
    mock_ollama.assert_called_once()
    assert result.score == 90

async def test_json_parse_failure_triggers_retry(mocker):
    """Test tenacity retry block detects malformed JSON and retries automatically."""
    # Arrange
    # First call returns invalid JSON string, second call returns valid JSON string
    mock_openai = mocker.patch(
        "backend.services.ai_engine._call_openai", 
        side_effect=["INVALID JSON FORMAT", '{"test": "success"}']
    )

    # Act
    result = await _generate_json("System prompt", "User prompt")

    # Assert
    # Verify tenacity fired exactly twice
    assert mock_openai.call_count == 2
    assert result["test"] == "success"
