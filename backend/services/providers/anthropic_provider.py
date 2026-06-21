import json
import logging
import os
from typing import Dict, Any

from .base import LLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "anthropic"

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Placeholder for Anthropic API implementation.
        Requires anthropic python package.
        """
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
            
            # Note: Anthropic doesn't have native json_object mode, so we rely on system prompt 
            # and potentially parse out markdown blocks if needed.
            response = await client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.content[0].text
            return json.loads(content)
        except ImportError:
            logger.error("anthropic package not installed. Cannot use AnthropicProvider.")
            raise ValueError("Anthropic package not installed.")
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
