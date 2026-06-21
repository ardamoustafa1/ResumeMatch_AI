"""Tests for core/metrics.py - MetricsTracker logging."""
import pytest
import logging
from backend.core.metrics import metrics, MetricsTracker


def test_log_llm_call(caplog):
    with caplog.at_level(logging.INFO, logger="metrics"):
        metrics.log_llm_call(
            model="gpt-4",
            latency_ms=123.45,
            tokens_estimated=500,
            cost_estimated=0.0012,
            success=True,
        )
    assert "metric=llm_call" in caplog.text
    assert "model=gpt-4" in caplog.text
    assert "latency_ms=123.45" in caplog.text
    assert "success=True" in caplog.text


def test_log_queue_processing(caplog):
    with caplog.at_level(logging.INFO, logger="metrics"):
        metrics.log_queue_processing(
            queue_name="analysis_queue",
            wait_time_ms=50.0,
            process_time_ms=320.0,
        )
    assert "metric=queue_job" in caplog.text
    assert "queue=analysis_queue" in caplog.text
    assert "wait_ms=50.00" in caplog.text
    assert "process_ms=320.00" in caplog.text


def test_log_api_request(caplog):
    with caplog.at_level(logging.INFO, logger="metrics"):
        metrics.log_api_request(
            path="/api/v1/analysis",
            method="POST",
            status_code=200,
            latency_ms=45.6,
        )
    assert "metric=api_request" in caplog.text
    assert "path=/api/v1/analysis" in caplog.text
    assert "method=POST" in caplog.text
    assert "status=200" in caplog.text
    assert "latency_ms=45.60" in caplog.text
