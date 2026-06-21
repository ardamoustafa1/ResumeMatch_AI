import pytest
from unittest.mock import MagicMock
from backend.services.extraction_service import (
    extract_text_from_pdf,
    extract_text_from_image,
    extract_document_text,
)

pytestmark = pytest.mark.asyncio

async def test_extract_text_from_pdf_success(mocker):
    mock_fitz = mocker.patch("backend.services.extraction_service.fitz_module.open")
    mock_doc = MagicMock()
    mock_doc.__len__.return_value = 2
    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "Page 1 Text"
    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "Page 2 Text"
    
    mock_doc.load_page.side_effect = [mock_page1, mock_page2]
    mock_fitz.return_value = mock_doc
    
    mock_settings = MagicMock()
    mock_settings.max_pdf_pages = 5
    mocker.patch("backend.services.extraction_service.settings", mock_settings)
    
    text = await extract_text_from_pdf(b"fake_pdf_bytes")
    assert text == "Page 1 Text\nPage 2 Text"
    mock_fitz.assert_called_once()

async def test_extract_text_from_pdf_limit_exceeded(mocker):
    mock_fitz = mocker.patch("backend.services.extraction_service.fitz_module.open")
    mock_doc = MagicMock()
    mock_doc.__len__.return_value = 10
    mock_fitz.return_value = mock_doc
    
    mock_settings = MagicMock()
    mock_settings.max_pdf_pages = 5
    mocker.patch("backend.services.extraction_service.settings", mock_settings)
    
    with pytest.raises(ValueError, match="Could not parse PDF file: PDF exceeds"):
        await extract_text_from_pdf(b"fake_pdf_bytes")

async def test_extract_text_from_image_success(mocker):
    mock_image_open = mocker.patch("backend.services.extraction_service.image_module.open")
    mock_img = MagicMock()
    mock_img.width = 100
    mock_img.height = 100
    mock_image_open.return_value = mock_img
    
    mock_tesseract = mocker.patch("backend.services.extraction_service.pytesseract_module.image_to_string")
    mock_tesseract.return_value = "Image Text"
    
    mock_settings = MagicMock()
    mock_settings.max_image_pixels = 20000
    mocker.patch("backend.services.extraction_service.settings", mock_settings)
    
    text = await extract_text_from_image(b"fake_image_bytes")
    assert text == "Image Text"
    mock_image_open.assert_called()

async def test_extract_text_from_image_limit_exceeded(mocker):
    mock_image_open = mocker.patch("backend.services.extraction_service.image_module.open")
    mock_img = MagicMock()
    mock_img.width = 2000
    mock_img.height = 2000
    mock_image_open.return_value = mock_img
    
    mock_settings = MagicMock()
    mock_settings.max_image_pixels = 20000
    mocker.patch("backend.services.extraction_service.settings", mock_settings)
    
    with pytest.raises(ValueError, match="Could not parse Image file: Image dimensions exceed"):
        await extract_text_from_image(b"fake_image_bytes")

async def test_extract_document_text_routing(mocker):
    mock_pdf = mocker.patch("backend.services.extraction_service.extract_text_from_pdf", return_value="PDF")
    mock_img = mocker.patch("backend.services.extraction_service.extract_text_from_image", return_value="IMG")
    
    assert await extract_document_text(b"...", "test.pdf", "application/pdf") == "PDF"
    assert await extract_document_text(b"...", "test.png", "image/png") == "IMG"
    
    with pytest.raises(ValueError, match="Unsupported file type"):
        await extract_document_text(b"...", "test.doc", "application/msword")
