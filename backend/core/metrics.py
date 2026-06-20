import logging
from datetime import datetime, timezone

logger = logging.getLogger("metrics")


class MetricsTracker:
    @staticmethod
    def log_llm_call(
        model: str,
        latency_ms: float,
        tokens_estimated: int,
        cost_estimated: float,
        success: bool,
    ):
        logger.info(
            "metric=llm_call model=%s latency_ms=%.2f tokens=%d cost=%.4f success=%s time=%s",
            model,
            latency_ms,
            tokens_estimated,
            cost_estimated,
            success,
            datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def log_queue_processing(
        queue_name: str, wait_time_ms: float, process_time_ms: float
    ):
        logger.info(
            "metric=queue_job queue=%s wait_ms=%.2f process_ms=%.2f time=%s",
            queue_name,
            wait_time_ms,
            process_time_ms,
            datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def log_api_request(path: str, method: str, status_code: int, latency_ms: float):
        logger.info(
            "metric=api_request path=%s method=%s status=%d latency_ms=%.2f time=%s",
            path,
            method,
            status_code,
            latency_ms,
            datetime.now(timezone.utc).isoformat(),
        )


metrics = MetricsTracker()
