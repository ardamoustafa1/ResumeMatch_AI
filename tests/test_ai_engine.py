import json

import pytest

from backend.models.schemas import MatchResult
from backend.services.ai_engine import _generate_json, analyze_cv_jd_match

pytestmark = pytest.mark.asyncio


async def test_match_score_returns_valid_range(mocker, sample_cv, sample_jd):
    response = {
        "score": 85,
        "matched_skills": ["Python"],
        "missing_skills": ["Kubernetes"],
        "improvement_suggestions": ["Add measurable platform outcomes"],
    }
    mocker.patch(
        "backend.services.ai_engine._call_groq",
        return_value=json.dumps(response),
    )

    result = await analyze_cv_jd_match(sample_cv, sample_jd)

    assert isinstance(result, MatchResult)
    assert result.score == 85


async def test_groq_falls_back_to_ollama(mocker, sample_cv, sample_jd):
    mocker.patch(
        "backend.services.ai_engine._call_groq",
        side_effect=RuntimeError("provider unavailable"),
    )
    ollama = mocker.patch(
        "backend.services.ai_engine._call_ollama",
        return_value=json.dumps(
            {
                "score": 90,
                "matched_skills": [],
                "missing_skills": [],
                "improvement_suggestions": [],
            }
        ),
    )

    result = await analyze_cv_jd_match(sample_cv, sample_jd)

    ollama.assert_called_once()
    assert result.score == 90


async def test_json_parse_failure_retries(mocker):
    groq = mocker.patch(
        "backend.services.ai_engine._call_groq",
        side_effect=["INVALID JSON", '{"test": "success"}'],
    )

    result = await _generate_json("system", "user")

    assert groq.call_count == 2
    assert result == {"test": "success"}
