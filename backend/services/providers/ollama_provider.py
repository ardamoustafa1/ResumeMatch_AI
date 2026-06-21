import os
import json
import logging
from typing import Dict, Any
import httpx
from backend.core.prometheus_metrics import llm_provider_requests_total
from backend.services.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self._base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._model = model or os.getenv("OLLAMA_MODEL", "llama3:8b")

    @property
    def name(self) -> str:
        return "ollama"

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        logger.info(f"Using Ollama provider with model {self._model}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.0},
                }
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
                llm_provider_requests_total.labels(provider=self.name, status="success").inc()
                data = response.json()
                content = data["message"]["content"]
                return json.loads(content)
        except Exception as e:
            llm_provider_requests_total.labels(provider=self.name, status="failure").inc()
            logger.warning(f"Ollama generation failed: {e}")
            raise
