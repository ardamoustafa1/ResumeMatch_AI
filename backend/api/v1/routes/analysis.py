import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from asyncpg import Connection

from backend.db.connection import get_db
from backend.db.queries import create_analysis, get_analysis
from backend.models.schemas import AnalysisRequest, AnalysisResponse
from backend.tasks.analysis_tasks import run_analysis_task

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def start_analysis(
    request: AnalysisRequest, 
    # Mock user_id injection. In a real app, this comes from an auth dependency.
    user_id: str = "00000000-0000-0000-0000-000000000000",
    conn: Connection = Depends(get_db)
):
    try:
        analysis_id = await create_analysis(
            conn=conn,
            user_id=user_id,
            cv_text=request.cv_text,
            jd_text=request.jd_text,
            company=request.company,
            recruiter_name=request.recruiter_name
        )
        
        # Enqueue the background task via Celery
        run_analysis_task.delay(analysis_id)
        
        return {
            "analysis_id": analysis_id,
            "status": "pending",
            "estimated_seconds": 30
        }
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to queue analysis", "code": "QUEUE_ERROR", "detail": str(e)}
        )

@router.get("/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    conn: Connection = Depends(get_db)
):
    try:
        record = await get_analysis(conn, analysis_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Analysis not found", "code": "NOT_FOUND"}
            )
            
        current_status = record["status"]
        
        if current_status == "completed":
            return AnalysisResponse(**record)
            
        elif current_status == "failed":
            error_detail = record.get("result", {}).get("error", "Unknown error") if record.get("result") else "Unknown error"
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error": "Analysis failed", "code": "ANALYSIS_FAILED", "detail": error_detail}
            )
            
        else:
            # For 'pending' or 'processing', direct client to WebSocket for progress.
            return {
                "id": record["id"],
                "status": current_status,
                "progress": "Check WebSocket for real-time updates."
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": str(e)}
        )
