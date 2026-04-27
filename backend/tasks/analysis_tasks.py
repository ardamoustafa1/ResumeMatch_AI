import asyncio
import logging
import os
from backend.tasks.celery_app import celery_app
from backend.tasks.progress_events import publish_progress_sync
import asyncpg
from backend.db.connection import DATABASE_URL
from backend.db.queries import get_analysis, update_analysis_result, get_telegram_config
from backend.models.schemas import AnalysisRequest, FullAnalysisResult
from backend.services.ai_engine import (
    analyze_cv_jd_match, 
    generate_outreach_messages, 
    generate_profile_improvements
)
from backend.services.telegram_service import (
    send_analysis_complete, 
    send_error_notification
)

logger = logging.getLogger(__name__)

async def _process_analysis(analysis_id: str) -> None:
    """Async wrapper executing the analysis pipeline and emitting events."""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        publish_progress_sync(analysis_id, "validating", 10)
        
        record = await get_analysis(conn, analysis_id)
        if not record:
            logger.error(f"Analysis {analysis_id} not found in DB.")
            await conn.close()
            return
        
        # Transition status
        await update_analysis_result(conn, analysis_id, "processing")
            
        # AI Pipeline
        publish_progress_sync(analysis_id, "analyzing_match", 30)
        
        request = AnalysisRequest(
            cv_text=record["cv_text"],
            jd_text=record["jd_text"],
            company=record.get("company"),
            recruiter_name=record.get("recruiter_name")
        )
        
        result = FullAnalysisResult()
        
        # 1. Match
        try:
            result.match_result = await analyze_cv_jd_match(request.cv_text, request.jd_text)
        except Exception as e:
            logger.error(f"Match failed: {e}")
        
        publish_progress_sync(analysis_id, "generating_messages", 60)
        
        # 2. Outreach
        if result.match_result:
            try:
                result.outreach_messages = await generate_outreach_messages(
                    request.cv_text, 
                    request.jd_text, 
                    request.company or "our company", 
                    request.recruiter_name or "a recruiter", 
                    result.match_result
                )
            except Exception as e:
                logger.error(f"Outreach failed: {e}")
                
        publish_progress_sync(analysis_id, "improving_profile", 85)
        
        # 3. Profile Improvements
        try:
            result.profile_improvements = await generate_profile_improvements(request.cv_text, request.jd_text)
        except Exception as e:
            logger.error(f"Profile improvements failed: {e}")
            
        final_data = result.model_dump()
        
        # Completion
        await update_analysis_result(conn, analysis_id, "completed", final_data)
        publish_progress_sync(analysis_id, "done", 100, data=final_data)
        
        # Telegram notification hook
        logger.info(f"Analysis {analysis_id} completed. Sending Telegram notification...")
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token:
            tg_config = await get_telegram_config(conn, record["user_id"])
            if tg_config and tg_config.get("chat_id"):
                await send_analysis_complete(
                    chat_id=tg_config["chat_id"],
                    bot_token=bot_token,
                    analysis_id=analysis_id,
                    company=request.company,
                    recruiter_name=request.recruiter_name,
                    result=result
                )

    except Exception as e:
        logger.error(f"Error processing analysis {analysis_id}: {e}")
        await update_analysis_result(conn, analysis_id, "failed", {"error": str(e)})
        
        # Send error notification
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token:
            # We need to re-fetch the record since it might have failed early
            record = await get_analysis(conn, analysis_id)
            if record and record.get("user_id"):
                tg_config = await get_telegram_config(conn, record["user_id"])
                if tg_config and tg_config.get("chat_id"):
                    await send_error_notification(
                        chat_id=tg_config["chat_id"],
                        bot_token=bot_token,
                        analysis_id=analysis_id,
                        error=str(e)
                    )
                    
        publish_progress_sync(analysis_id, "failed", 0, data={"error": str(e)})
        raise e
    finally:
        await conn.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def run_analysis_task(self, analysis_id: str):
    """
    Celery task entrypoint. Bridges the sync Celery worker context with the async AI pipeline.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_process_analysis(analysis_id))
    except Exception as exc:
        logger.error(f"Celery task failed, retrying. Analysis ID: {analysis_id}")
        self.retry(exc=exc)
    finally:
        loop.close()
