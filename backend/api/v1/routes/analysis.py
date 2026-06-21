import logging

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Security
from uuid import UUID

from backend.api.deps import get_current_user, Scope
from backend.core.rate_limit import limiter
from backend.db.connection import get_db
from backend.db.queries import (
    create_analysis,
    get_analysis,
    get_user_analyses,
    log_audit_event,
    update_analysis_result,
)
from backend.models.schemas import AnalysisRequest, AnalysisResponse
from backend.tasks.analysis_tasks import run_analysis_task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/demo")
async def demo_analysis():
    import uuid

    mock_id = str(uuid.uuid4())
    mock_data = {
        "analysis_id": mock_id,
        "status": "completed",
        "result": {
            "match_result": {
                "score": 92,
                "matched_skills": [
                    "React",
                    "FastAPI",
                    "PostgreSQL",
                    "Docker",
                    "TypeScript",
                ],
                "missing_skills": ["GraphQL", "Kubernetes"],
                "improvement_suggestions": [
                    "Highlight your REST API design experience",
                    "Add metrics on how your Dockerization improved build times",
                ],
            },
            "outreach_messages": {
                "dm_first_contact": "Hi! I noticed your team is building a scalable career copilot. My background in Next.js and FastAPI directly aligns with the stack mentioned in the job description.",
                "dm_follow_up": "Just floating this up! Let me know if you have 5 minutes this week.",
                "connection_note": "Hi! I'm an engineer specializing in React & FastAPI, would love to connect and discuss the open backend role.",
            },
            "profile_improvements": {
                "headline_before": "Software Developer",
                "headline_after": "Senior Full-Stack Engineer | React & Python | Building Scalable SaaS",
                "about_section": "I build robust, local-first applications using Next.js and FastAPI. My focus is on deterministic outcomes and secure architectures.",
            },
            "errors": {},
        },
    }
    return mock_data


@router.post("", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def start_analysis(
    request: Request,
    payload: AnalysisRequest,
    current_user: dict = Security(
        get_current_user, scopes=[Scope.WRITE_ANALYSIS, Scope.EXTENSION]
    ),
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


@router.get("")
async def list_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Security(
        get_current_user, scopes=[Scope.READ_ANALYSIS, Scope.EXTENSION]
    ),
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
    analysis_id: UUID,
    current_user: dict = Security(
        get_current_user, scopes=[Scope.READ_ANALYSIS, Scope.EXTENSION]
    ),
    conn: Connection = Depends(get_db),
):
    analysis_id_str = str(analysis_id)
    try:
        record = await get_analysis(conn, analysis_id_str)
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
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Security(
        get_current_user, scopes=[Scope.WRITE_ANALYSIS, Scope.EXTENSION]
    ),
    conn: Connection = Depends(get_db),
):
    deleted = await conn.execute(
        "DELETE FROM analyses WHERE id = $1 AND user_id = $2",
        analysis_id,
        current_user["id"],
    )
    if deleted == "DELETE 0":
        raise HTTPException(
            status_code=404, detail="Analysis not found or unauthorized."
        )
    await log_audit_event(
        conn,
        "analysis.deleted",
        user_id=str(current_user["id"]),
        ip_address=None,
        metadata={"analysis_id": analysis_id},
    )

    return {"status": "deleted"}


@router.patch("/{analysis_id}")
async def update_analysis(
    analysis_id: UUID,
    payload: dict,
    current_user: dict = Security(
        get_current_user, scopes=[Scope.WRITE_ANALYSIS, Scope.EXTENSION]
    ),
    conn: Connection = Depends(get_db),
):
    analysis_id_str = str(analysis_id)
    record = await get_analysis(conn, analysis_id_str)
    if not record or str(record["user_id"]) != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or unauthorized.",
        )
    if record["status"] not in {"completed", "partial_completed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update completed analyses.",
        )

    import json
    await conn.execute(
        "UPDATE analyses SET result = $1 WHERE id = $2",
        json.dumps(payload),
        analysis_id_str,
    )
    return {"status": "updated"}
