import logging

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, Security

from backend.api.deps import get_current_user, Scope
from backend.core.config import settings
from backend.core.rate_limit import limiter
from backend.services.extraction_service import extract_document_text

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}


async def _read_limited(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the {settings.max_upload_bytes // 1024 // 1024} MB limit.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/")
@limiter.limit("10/hour")
async def extract_text(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Security(get_current_user, scopes=[Scope.EXTENSION]),
):
    del current_user
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if (file.content_type or "") not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    try:
        file_bytes = await _read_limited(file)
        extracted_text = await extract_document_text(
            file_bytes,
            file.filename,
            file.content_type or "",
        )
        if not extracted_text:
            raise ValueError("No text could be extracted from the document.")
        return {"filename": file.filename, "extracted_text": extracted_text}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Document extraction failed")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during extraction",
        )
