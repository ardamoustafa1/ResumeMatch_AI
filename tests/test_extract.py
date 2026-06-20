import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_extract_text_no_file(client: AsyncClient):
    response = await client.post("/api/v1/extract-text/")
    assert response.status_code == 422  # validation error

@pytest.mark.asyncio
async def test_extract_text_unsupported_type(client: AsyncClient):
    files = {"file": ("test.txt", b"hello", "text/plain")}
    response = await client.post("/api/v1/extract-text/", files=files)
    assert response.status_code == 415

@pytest.mark.asyncio
async def test_extract_text_success(client: AsyncClient, mocker):
    mocker.patch("backend.api.v1.routes.extract.extract_document_text", return_value="Some extracted text")
    files = {"file": ("test.pdf", b"pdfcontent", "application/pdf")}
    response = await client.post("/api/v1/extract-text/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filename": "test.pdf", "extracted_text": "Some extracted text"}
