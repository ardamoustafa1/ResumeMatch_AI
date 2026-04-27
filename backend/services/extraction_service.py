import io
import logging
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

logger = logging.getLogger(__name__)

async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    if not fitz:
        raise RuntimeError("PyMuPDF (fitz) is not installed.")
    
    try:
        # Open PDF from memory
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise ValueError(f"Could not parse PDF file: {e}")

async def extract_text_from_image(file_bytes: bytes) -> str:
    """Extracts text from an image using Tesseract OCR."""
    if not pytesseract or not Image:
        raise RuntimeError("pytesseract or Pillow is not installed.")
    
    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Optional: pre-processing can go here if needed
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from image: {e}")
        raise ValueError(f"Could not parse Image file: {e}")

async def extract_document_text(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Orchestrates extraction based on file type."""
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return await extract_text_from_pdf(file_bytes)
    elif content_type.startswith("image/") or filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return await extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")
