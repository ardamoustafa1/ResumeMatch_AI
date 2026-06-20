import asyncio
import logging
import os

from celery.signals import worker_process_init, worker_process_shutdown

from backend.db.connection import db_pool
from backend.db.queries import (
    get_analysis,
    get_telegram_config,
    update_analysis_result,
)
from backend.models.schemas import AnalysisRequest, FullAnalysisResult
from backend.services.ai_engine import (
    analyze_cv_jd_match,
    generate_outreach_messages,
    generate_profile_improvements,
)
from backend.services.telegram_service import (
    send_analysis_complete,
    send_error_notification,
)
from backend.tasks.celery_app import celery_app
from backend.tasks.progress_events import publish_progress_sync

logger = logging.getLogger(__name__)


# Global persistent event loop for the Celery worker process
celery_worker_loop = None


@worker_process_init.connect
def init_worker_loop(**kwargs):
    global celery_worker_loop
    celery_worker_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(celery_worker_loop)
    celery_worker_loop.run_until_complete(db_pool.connect())
    logger.info("Celery worker process initialized persistent event loop and DB pool.")


@worker_process_shutdown.connect
def shutdown_worker_loop(**kwargs):
    global celery_worker_loop
    if celery_worker_loop and db_pool.pool:
        celery_worker_loop.run_until_complete(db_pool.disconnect())
        celery_worker_loop.close()
        logger.info("Celery worker process shut down event loop and DB pool.")


async def _process_analysis(analysis_id: str) -> None:
    """Run an idempotent analysis attempt and persist a complete or partial result."""
    if db_pool.pool is None:
        raise RuntimeError("DB pool not initialized in Celery worker.")
        
    # Phase 1: Fetch and Lock
    async with db_pool.pool.acquire() as conn:
        record = await get_analysis(conn, analysis_id)
        if not record:
            raise LookupError(f"Analysis {analysis_id} does not exist.")
        if record["status"] in {"completed", "partial_completed"}:
            logger.info("Analysis %s is already complete; skipping duplicate task.", analysis_id)
            return
            
        # Optional: Lock by setting to 'processing' and checking if it was already processing
        # Since it's idempotency, if it is processing we just update it anyway.
        publish_progress_sync(analysis_id, "validating", 10)
        await update_analysis_result(conn, analysis_id, "processing")
        
        request = AnalysisRequest(
            cv_text=record["cv_text"],
            jd_text=record["jd_text"],
            company=record.get("company"),
            recruiter_name=record.get("recruiter_name"),
        )
        user_id = record["user_id"]

    # Phase 2: LLM Operations (without holding DB connection)
    result = FullAnalysisResult()

    publish_progress_sync(analysis_id, "analyzing_match", 30)
    result.match_result = await analyze_cv_jd_match(
        request.cv_text,
        request.jd_text,
    )

    publish_progress_sync(analysis_id, "generating_messages", 60)
    try:
        result.outreach_messages = await generate_outreach_messages(
            request.cv_text,
            request.jd_text,
            request.company or "the company",
            request.recruiter_name or "the recruiter",
            result.match_result,
        )
    except Exception:
        logger.exception("Outreach generation failed for %s", analysis_id)
        result.errors["outreach_messages"] = "Outreach messages could not be generated."

    publish_progress_sync(analysis_id, "improving_profile", 85)
    try:
        result.profile_improvements = await generate_profile_improvements(
            request.cv_text,
            request.jd_text,
        )
    except Exception:
        logger.exception("Profile generation failed for %s", analysis_id)
        result.errors["profile_improvements"] = "Profile improvements could not be generated."

    final_data = result.model_dump()
    final_status = "partial_completed" if result.errors else "completed"
    
    # Phase 3: Save Results
    async with db_pool.pool.acquire() as conn:
        await update_analysis_result(conn, analysis_id, final_status, final_data)
        publish_progress_sync(
            analysis_id,
            final_status,
            100,
            data=final_data,
        )

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token:
            telegram_config = await get_telegram_config(conn, user_id)
            if telegram_config and telegram_config.get("chat_id"):
                await send_analysis_complete(
                    chat_id=telegram_config["chat_id"],
                    bot_token=bot_token,
                    analysis_id=analysis_id,
                    company=request.company or "Not specified",
                    recruiter_name=request.recruiter_name or "Not specified",
                    result=result,
                )


async def _mark_analysis_failed(analysis_id: str, error: Exception) -> None:
    if db_pool.pool is None:
        return
    async with db_pool.pool.acquire() as conn:
        record = await get_analysis(conn, analysis_id)
        if record and record["status"] not in {"completed", "partial_completed"}:
            await update_analysis_result(
                conn,
                analysis_id,
                "failed",
                {"error": "Analysis could not be completed after multiple attempts."},
            )
            publish_progress_sync(
                analysis_id,
                "failed",
                0,
                data={"error": "Analysis could not be completed."},
            )
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if bot_token:
                telegram_config = await get_telegram_config(conn, record["user_id"])
                if telegram_config and telegram_config.get("chat_id"):
                    await send_error_notification(
                        chat_id=telegram_config["chat_id"],
                        bot_token=bot_token,
                        analysis_id=analysis_id,
                        error="Analysis could not be completed.",
                    )
        logger.error("Analysis %s permanently failed: %s", analysis_id, error)


def _run(coroutine) -> None:
    global celery_worker_loop
    # Fallback in case task is run eagerly or outside standard worker
    if celery_worker_loop is None:
        celery_worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(celery_worker_loop)
        celery_worker_loop.run_until_complete(db_pool.connect())

    celery_worker_loop.run_until_complete(coroutine)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    acks_late=True,
    reject_on_worker_lost=True,
)
def run_analysis_task(self, analysis_id: str):
    try:
        _run(_process_analysis(analysis_id))
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            _run(_mark_analysis_failed(analysis_id, exc))
            raise
        retry_delay = min(60, 5 * (2**self.request.retries))
        raise self.retry(exc=exc, countdown=retry_delay)


@celery_app.task(name="backend.tasks.analysis_tasks.purge_old_data_task")
def purge_old_data_task() -> None:
    """Scheduled task to purge analysis data older than 30 days for GDPR compliance."""
    from scripts.purge_old_data import purge_old_data
    import asyncio
    asyncio.run(purge_old_data())
