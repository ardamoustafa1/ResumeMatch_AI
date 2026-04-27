import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "networkforge",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.tasks.analysis_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=4,
    task_routes={
        "backend.tasks.analysis_tasks.run_analysis_task": {"queue": "high_priority"}
    },
    beat_schedule={
        # Hook for future scheduled tasks, e.g., weekly summaries or retention cleanup
    }
)
