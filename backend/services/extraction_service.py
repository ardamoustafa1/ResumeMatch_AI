import asyncio
import io
import logging

import fitz as fitz_module
import pytesseract as pytesseract_module
from PIL import Image as image_module

from backend.core.config import settings

logger = logging.getLogger(__name__)


async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    try:
        def _load_pdf():
            doc = fitz_module.open(stream=file_bytes, filetype="pdf")
            if len(doc) > settings.max_pdf_pages:
                raise ValueError(f"PDF exceeds the {settings.max_pdf_pages} page limit.")
            res = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                res += page.get_text() + "\n"
            return res.strip()
            
        text = await asyncio.to_thread(_load_pdf)
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise ValueError(f"Could not parse PDF file: {e}")


async def extract_text_from_image(file_bytes: bytes) -> str:
    """Extracts text from an image using Tesseract OCR."""
    try:
        def _load_image():
            image_module.MAX_IMAGE_PIXELS = settings.max_image_pixels
            img = image_module.open(io.BytesIO(file_bytes))
            if img.width * img.height > settings.max_image_pixels:
                raise ValueError("Image dimensions exceed the configured safety limit.")
            img.verify()
            img = image_module.open(io.BytesIO(file_bytes))
            return pytesseract_module.image_to_string(img).strip()

        text = await asyncio.to_thread(_load_image)
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from image: {e}")
        raise ValueError(f"Could not parse Image file: {e}")


async def extract_document_text(
    file_bytes: bytes, filename: str, content_type: str
) -> str:
    """Orchestrates extraction based on file type."""
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return await extract_text_from_pdf(file_bytes)
    elif content_type.startswith("image/") or filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):
        return await extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")
