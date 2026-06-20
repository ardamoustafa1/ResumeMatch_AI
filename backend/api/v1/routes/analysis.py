import logging

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.api.deps import get_current_user
from backend.core.rate_limit import limiter
from backend.db.connection import get_db
from backend.db.queries import (
    create_analysis,
    delete_analysis,
    get_analysis,
    get_user_analyses,
    update_analysis_result,
)
from backend.models.schemas import AnalysisRequest, AnalysisResponse
from backend.tasks.analysis_tasks import run_analysis_task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def start_analysis(
    request: Request,
    payload: AnalysisRequest,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    try:
        analysis_id = await create_analysis(
            conn=conn,
            user_id=str(current_user["id"]),
            cv_text=payload.cv_text,
            jd_text=payload.jd_text,
            company=payload.company,
            recruiter_name=payload.recruiter_name,
        )
        try:
            run_analysis_task.delay(analysis_id)
        except Exception:
            await update_analysis_result(
                conn,
                analysis_id,
                "failed",
                {"error": "The analysis queue is currently unavailable."},
            )
            raise

        return {
            "analysis_id": analysis_id,
            "status": "pending",
            "estimated_seconds": 30,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to start analysis")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "Failed to queue analysis", "code": "QUEUE_ERROR"},
        )


@router.get("/export")
async def export_analyses(
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    """Export all analysis data for GDPR/Data Portability compliance."""
    records = await get_user_analyses(
        conn,
        str(current_user["id"]),
        limit=1000,
        offset=0,
    )
    return {"data": records}


@router.get("")
async def list_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    return {
        "items": await get_user_analyses(
            conn,
            str(current_user["id"]),
            limit=limit,
            offset=offset,
        ),
        "limit": limit,
        "offset": offset,
    }


@router.get("/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    try:
        record = await get_analysis(conn, analysis_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Analysis not found", "code": "NOT_FOUND"},
            )
        if str(record["user_id"]) != str(current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Not authorized to access this analysis",
                    "code": "FORBIDDEN",
                },
            )

        current_status = record["status"]

        if current_status in {"completed", "partial_completed"}:
            return AnalysisResponse(**record)

        if current_status == "failed":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error": "Analysis failed", "code": "ANALYSIS_FAILED"},
            )

        return {
            "id": record["id"],
            "status": current_status,
            "progress": "Connect to the analysis WebSocket for real-time updates.",
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to retrieve analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "code": "INTERNAL_ERROR"},
        )

@router.delete("/{analysis_id}")
async def delete_analysis_endpoint(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db)
):
    try:
        import uuid
        val = uuid.UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis ID.")
    
    deleted = await conn.execute(
        "DELETE FROM analyses WHERE id = $1 AND user_id = $2",
        val,
        current_user["id"]
    )
    if deleted == "DELETE 0":
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized.")
        
    return {"status": "deleted"}
