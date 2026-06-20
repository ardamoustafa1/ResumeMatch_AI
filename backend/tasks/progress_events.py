import json
import os

import redis as sync_redis
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

sync_redis_client = sync_redis.from_url(REDIS_URL)
async_redis_client = redis.from_url(REDIS_URL)

STEP_MESSAGES = {
    "validating": "Validating your CV and job description",
    "analyzing_match": "Calculating the role match",
    "generating_messages": "Writing personalized outreach messages",
    "improving_profile": "Preparing profile improvements",
    "done": "Analysis completed",
    "completed": "Analysis completed",
    "partial_completed": "Analysis completed with partial results",
    "failed": "Analysis failed",
}


def _event_name(step: str) -> str:
    if step in {"completed", "done", "partial_completed"}:
        return "completed"
    if step == "failed":
        return "failed"
    return "progress"


def _message(
    analysis_id: str,
    step: str,
    percent: int,
    data: dict | None,
) -> dict:
    return {
        "analysis_id": analysis_id,
        "event": _event_name(step),
        "step": step,
        "progress": percent,
        "message": STEP_MESSAGES.get(step, step.replace("_", " ").title()),
        "data": data or {},
    }


def publish_progress_sync(
    analysis_id: str,
    step: str,
    percent: int,
    data: dict | None = None,
) -> None:
    channel = f"analysis_progress:{analysis_id}"
    sync_redis_client.publish(
        channel,
        json.dumps(_message(analysis_id, step, percent, data)),
    )


async def publish_progress(
    analysis_id: str,
    step: str,
    percent: int,
    data: dict | None = None,
) -> None:
    channel = f"analysis_progress:{analysis_id}"
    await async_redis_client.publish(
        channel,
        json.dumps(_message(analysis_id, step, percent, data)),
    )
