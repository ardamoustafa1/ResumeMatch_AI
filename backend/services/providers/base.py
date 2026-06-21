from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers in the AI Engine.
    Enforces a common interface for text and JSON generation.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g., 'groq', 'ollama')."""
        pass

    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generates a JSON response from the LLM based on the given prompts.
        Must return a parsed dictionary. Raises exceptions on failure.
        """
        pass
