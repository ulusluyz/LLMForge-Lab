import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel
import requests

T = TypeVar("T", bound=BaseModel)

class APIProvider(ABC):
    """Abstract Base Class for Intelligence API Providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        """Generate a response matching a validated Pydantic schema."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """Generate unstructured text."""
        pass


class GeminiProvider(APIProvider):
    """Provider adapter for Google Gemini API."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = config.get("model_name") or os.environ.get("LLMFORGE_INTELLIGENCE_MODEL", "gemini-1.5-flash")

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        schema_json = json.dumps(response_schema.model_json_schema())
        augmented_prompt = f"{prompt}\n\nYou MUST respond strictly in valid JSON format matching this schema:\n{schema_json}"

        text = await self.generate_text(augmented_prompt, system_instruction)

        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        data = json.loads(clean_text)
        return response_schema.model_validate(data)

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        contents = [{"parts": [{"text": prompt}]}]
        payload: Dict[str, Any] = {"contents": contents}

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        res = await asyncio.to_thread(requests.post, url, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                raise ValueError(f"Malformed response structure from Gemini API: {data}")
        else:
            raise RuntimeError(f"Gemini API returned status {res.status_code}: {res.text}")


class MockProvider(APIProvider):
    """Deterministic Mock Provider for CI/Testing."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.responses: Dict[str, Any] = config.get("responses", {})

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        schema_name = response_schema.__name__
        if schema_name in self.responses:
            data = self.responses[schema_name]
            if isinstance(data, response_schema):
                return data
            return response_schema.model_validate(data)

        return response_schema.construct()

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        return self.responses.get("default_text", "Mock Intelligence API Response")
