import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.extraction_service import extract_document_text

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def extract_text(file: UploadFile = File(...)):
    """
    Receives a PDF or Image file, extracts text via OCR or PDF parsing, and returns it.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
        
    try:
        file_bytes = await file.read()
        extracted_text = await extract_document_text(file_bytes, file.filename, file.content_type or "")
        
        if not extracted_text:
            raise ValueError("No text could be extracted from the document.")
            
        return {"filename": file.filename, "extracted_text": extracted_text}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error extracting text from {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during extraction")
