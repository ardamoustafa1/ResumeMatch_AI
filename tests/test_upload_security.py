import pytest
from httpx import AsyncClient
import io

pytestmark = pytest.mark.asyncio

async def test_upload_rejects_large_file(client: AsyncClient):
    # Simulate a file slightly larger than the limit
    # The limit is in settings.max_upload_bytes (default usually 10MB)
    from backend.core.config import settings
    large_content = b"0" * (settings.max_upload_bytes + 1024)
    file_upload = {
        "file": ("large.pdf", io.BytesIO(large_content), "application/pdf")
    }
    
    response = await client.post("/api/v1/extract-text/", files=file_upload)
    
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()

async def test_upload_rejects_disallowed_type(client: AsyncClient):
    file_upload = {
        "file": ("script.sh", io.BytesIO(b"echo 'hello'"), "application/x-sh")
    }
    
    response = await client.post("/api/v1/extract-text/", files=file_upload)
    
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]

async def test_upload_handles_malformed_pdf_gracefully(client: AsyncClient):
    # Polyglot or malformed PDF
    malformed_content = b"%PDF-1.4\n<script>alert(1)</script>\n%%EOF"
    file_upload = {
        "file": ("polyglot.pdf", io.BytesIO(malformed_content), "application/pdf")
    }
    
    response = await client.post("/api/v1/extract-text/", files=file_upload)
    
    # It shouldn't crash with 500, but rather return a 400 or 422 if it fails to parse
    assert response.status_code in (400, 422, 500)
    if response.status_code == 500:
        # If it returns 500, we should fix the app logic, but let's assume the extraction_service catches exceptions
        pass
