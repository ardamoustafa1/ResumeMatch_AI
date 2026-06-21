import os
import json
import logging
from typing import Dict, Any
from groq import AsyncGroq
from backend.core.prometheus_metrics import llm_provider_requests_total
from backend.services.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key or os.getenv("GROQ_API_KEY")
        self._model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.client = AsyncGroq(api_key=self._api_key) if self._api_key else None

    @property
    def name(self) -> str:
        return "groq"

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("GROQ_API_KEY is not set.")

        try:
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            llm_provider_requests_total.labels(provider=self.name, status="success").inc()
            content = response.choices[0].message.content or ""
            return json.loads(content)
        except Exception as e:
            llm_provider_requests_total.labels(provider=self.name, status="failure").inc()
            logger.warning(f"Groq generation failed: {e}")
            raise
