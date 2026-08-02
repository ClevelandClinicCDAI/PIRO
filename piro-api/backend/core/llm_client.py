"""LLM client abstraction for the PIRO Extraction Suite.

Provider is controlled entirely by environment variables — callers never
select the provider at runtime (PHI compliance).

Supported providers (configured via LLM_PROVIDER env var):
  - ollama      (default) — local Ollama server, HIPAA-safe
  - openai      — OpenAI API (requires OPENAI_API_KEY + BAA)
  - anthropic   — Anthropic API (requires ANTHROPIC_API_KEY + BAA)
  - azure       — Azure OpenAI / AI Services (requires LLM_API_KEY + BAA)
  - generic     — Any OpenAI-compatible endpoint
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx
from logger import logger


# ──────────────────────────────────────────────────────────────────────────────
# Response dataclass
# ──────────────────────────────────────────────────────────────────────────────

class FieldExtraction:
    __slots__ = ("value", "confidence", "provenance")

    def __init__(
        self,
        value: Any,
        confidence: Optional[float],
        provenance: Optional[str],
    ) -> None:
        self.value = value
        self.confidence = confidence
        self.provenance = provenance

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "confidence": self.confidence,
            "provenance": self.provenance,
        }


ExtractionResponse = Dict[str, FieldExtraction]


# ──────────────────────────────────────────────────────────────────────────────
# System prompt helpers
# ──────────────────────────────────────────────────────────────────────────────

_EXTRACTION_SYSTEM_PROMPT = """You are a medical information extraction assistant for a pathology reporting system.

Your task is to extract structured fields from pathology report text according to a JSON Schema.

CRITICAL RULES:
1. If you cannot find clear evidence for a field value, return null. Never guess or infer beyond what the text states.
2. Null is always better than a wrong answer. Accuracy is paramount.
3. For categorical fields, return only one of the specified enum values or null.
4. For boolean fields, return true or false only if clearly stated; otherwise null.
5. Extract the shortest exact quote from the report that supports the value (provenance).
6. Return a confidence score 0.0–1.0 reflecting your certainty:
   - 0.9–1.0: explicitly stated
   - 0.7–0.89: clearly implied
   - 0.5–0.69: uncertain
   - < 0.5: do not return — use null instead

Return a JSON object where each key is a field name and each value has this structure:
{
  "field_name": {
    "value": <extracted value matching the schema type, or null>,
    "confidence": <float 0.0-1.0, or null if value is null>,
    "provenance": "<shortest exact quote from the report supporting the value, or null>"
  }
}"""

_SUGGEST_SYSTEM_PROMPT = """You are a medical informatics expert helping clinicians design structured data extraction schemas for pathology reports.

Given a sample pathology report, suggest a list of structured fields that could be consistently extracted from similar reports.

For each field return a JSON object with:
- name: snake_case field name
- type: one of "text", "categorical", "boolean", "number", "date"
- hint: plain-English extraction instruction (1-2 sentences, mention standards if applicable e.g. WHO 2021)
- enum_values: list of allowed values for categorical fields (null otherwise)
- minimum: minimum value for number fields (null otherwise)
- maximum: maximum value for number fields (null otherwise)

Return a JSON array of field suggestion objects. Suggest 5-15 fields."""


def _build_extraction_user_prompt(report_text: str, schema: dict) -> str:
    schema_str = json.dumps(schema, indent=2)
    return (
        f"Extract the following fields from this pathology report.\n\n"
        f"JSON Schema:\n{schema_str}\n\n"
        f"Report text:\n{report_text}"
    )


def _parse_json_from_response(text: str) -> Any:
    """Extract JSON from LLM response, handling markdown code fences."""
    text = text.strip()
    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1)
    return json.loads(text)


def _normalize_extraction_response(raw: Any, schema: dict) -> ExtractionResponse:
    """Normalize raw LLM JSON into ExtractionResponse, handling partial/malformed output."""
    result: ExtractionResponse = {}
    if not isinstance(raw, dict):
        return result
    for field_name in schema.keys():
        field_data = raw.get(field_name, {})
        if isinstance(field_data, dict):
            value = field_data.get("value")
            confidence = field_data.get("confidence")
            provenance = field_data.get("provenance")
        else:
            # LLM returned a bare value instead of the nested structure
            value = field_data if field_data != "" else None
            confidence = None
            provenance = None

        # Enforce null-over-hallucination: drop low-confidence values
        if confidence is not None and float(confidence) < 0.5:
            value = None
            confidence = None
            provenance = None

        result[field_name] = FieldExtraction(
            value=value,
            confidence=float(confidence) if confidence is not None else None,
            provenance=str(provenance) if provenance else None,
        )
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Abstract base class
# ──────────────────────────────────────────────────────────────────────────────

class LLMClient(ABC):
    """Abstract LLM client. All providers must implement these two methods."""

    @abstractmethod
    async def extract(
        self, report_text: str, schema: dict
    ) -> ExtractionResponse:
        """Extract structured fields from a pathology report.

        Returns a dict mapping field_name → FieldExtraction.
        Values are null when evidence is absent or confidence is low.
        """

    @abstractmethod
    async def suggest_fields(self, sample_text: str) -> List[dict]:
        """Given a sample report, suggest a list of extraction field definitions."""


# ──────────────────────────────────────────────────────────────────────────────
# Ollama implementation
# ──────────────────────────────────────────────────────────────────────────────

class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def _chat(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]

    async def extract(self, report_text: str, schema: dict) -> ExtractionResponse:
        user_prompt = _build_extraction_user_prompt(report_text, schema)
        raw_text = await self._chat(_EXTRACTION_SYSTEM_PROMPT, user_prompt)
        raw = _parse_json_from_response(raw_text)
        return _normalize_extraction_response(raw, schema)

    async def suggest_fields(self, sample_text: str) -> List[dict]:
        user_prompt = f"Suggest extraction fields for this pathology report:\n\n{sample_text}"
        raw_text = await self._chat(_SUGGEST_SYSTEM_PROMPT, user_prompt)
        raw = _parse_json_from_response(raw_text)
        return raw if isinstance(raw, list) else []


# ──────────────────────────────────────────────────────────────────────────────
# OpenAI implementation
# ──────────────────────────────────────────────────────────────────────────────

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str, timeout: float = 120.0) -> None:
        try:
            import openai  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "openai package is not installed. Run: pip install openai"
            )
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def _chat_json(self, system: str, user: str, response_schema: Optional[dict] = None) -> str:
        import openai

        client = openai.AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)
        kwargs: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
        }
        if response_schema:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "extraction_response",
                    "schema": response_schema,
                    "strict": True,
                },
            }
        else:
            kwargs["response_format"] = {"type": "json_object"}

        resp = await client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content

    def _build_openai_response_schema(self, schema: dict) -> dict:
        """Build the OpenAI response_format JSON schema from the extraction schema."""
        properties = {}
        for field_name in schema.keys():
            properties[field_name] = {
                "type": "object",
                "properties": {
                    "value": {},
                    "confidence": {"type": ["number", "null"]},
                    "provenance": {"type": ["string", "null"]},
                },
                "required": ["value", "confidence", "provenance"],
                "additionalProperties": False,
            }
        return {
            "type": "object",
            "properties": properties,
            "required": list(schema.keys()),
            "additionalProperties": False,
        }

    async def extract(self, report_text: str, schema: dict) -> ExtractionResponse:
        user_prompt = _build_extraction_user_prompt(report_text, schema)
        response_schema = self._build_openai_response_schema(schema)
        raw_text = await self._chat_json(
            _EXTRACTION_SYSTEM_PROMPT, user_prompt, response_schema
        )
        raw = _parse_json_from_response(raw_text)
        return _normalize_extraction_response(raw, schema)

    async def suggest_fields(self, sample_text: str) -> List[dict]:
        user_prompt = f"Suggest extraction fields for this pathology report:\n\n{sample_text}"
        raw_text = await self._chat_json(_SUGGEST_SYSTEM_PROMPT, user_prompt)
        raw = _parse_json_from_response(raw_text)
        return raw if isinstance(raw, list) else []


# ──────────────────────────────────────────────────────────────────────────────
# Anthropic implementation
# ──────────────────────────────────────────────────────────────────────────────

class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, model: str, timeout: float = 120.0) -> None:
        try:
            import anthropic  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "anthropic package is not installed. Run: pip install anthropic"
            )
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def _build_extraction_tool(self, schema: dict) -> dict:
        """Build an Anthropic tool definition that enforces structured extraction output."""
        properties = {}
        for field_name, field_def in schema.items():
            field_type = field_def.get("type", "string")
            prop: dict = {"description": field_def.get("description", "")}
            if field_type == "boolean":
                prop["type"] = ["boolean", "null"]
            elif field_type == "number":
                prop["type"] = ["number", "null"]
                if "minimum" in field_def:
                    prop["minimum"] = field_def["minimum"]
                if "maximum" in field_def:
                    prop["maximum"] = field_def["maximum"]
            elif "enum" in field_def:
                prop["type"] = ["string", "null"]
                prop["enum"] = field_def["enum"] + [None]
            else:
                prop["type"] = ["string", "null"]

            properties[field_name] = {
                "type": "object",
                "properties": {
                    "value": prop,
                    "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                    "provenance": {"type": ["string", "null"]},
                },
                "required": ["value", "confidence", "provenance"],
            }

        return {
            "name": "extract_medical_data",
            "description": "Extract structured medical data from a pathology report",
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": list(schema.keys()),
            },
        }

    async def extract(self, report_text: str, schema: dict) -> ExtractionResponse:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.api_key, timeout=self.timeout)
        tool = self._build_extraction_tool(schema)
        user_prompt = _build_extraction_user_prompt(report_text, schema)

        resp = await client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=_EXTRACTION_SYSTEM_PROMPT,
            tools=[tool],
            tool_choice={"type": "tool", "name": "extract_medical_data"},
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Tool use response: find the tool_use block
        tool_use_block = next(
            (b for b in resp.content if b.type == "tool_use"), None
        )
        if tool_use_block is None:
            return {}

        raw = tool_use_block.input
        return _normalize_extraction_response(raw, schema)

    async def suggest_fields(self, sample_text: str) -> List[dict]:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.api_key, timeout=self.timeout)
        user_prompt = f"Suggest extraction fields for this pathology report:\n\n{sample_text}"

        resp = await client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=_SUGGEST_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = resp.content[0].text
        raw = _parse_json_from_response(raw_text)
        return raw if isinstance(raw, list) else []


# ──────────────────────────────────────────────────────────────────────────────
# Generic HTTP client (for LLaMA.cpp, vLLM, Qwen, etc. OpenAI-compatible APIs)
# ──────────────────────────────────────────────────────────────────────────────

class GenericOpenAICompatibleClient(LLMClient):
    """For any OpenAI-compatible API endpoint (vLLM, LM Studio, LLaMA.cpp server, Qwen, etc.)"""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "not-needed",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    async def _chat(self, system: str, user: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def extract(self, report_text: str, schema: dict) -> ExtractionResponse:
        user_prompt = _build_extraction_user_prompt(report_text, schema)
        raw_text = await self._chat(_EXTRACTION_SYSTEM_PROMPT, user_prompt)
        raw = _parse_json_from_response(raw_text)
        return _normalize_extraction_response(raw, schema)

    async def suggest_fields(self, sample_text: str) -> List[dict]:
        user_prompt = f"Suggest extraction fields for this pathology report:\n\n{sample_text}"
        raw_text = await self._chat(_SUGGEST_SYSTEM_PROMPT, user_prompt)
        raw = _parse_json_from_response(raw_text)
        return raw if isinstance(raw, list) else []


class AzureOpenAIClient(LLMClient):
    """Azure OpenAI / Azure AI Services client.

    Constructs the Azure-specific URL:
      {base_url}/openai/deployments/{model}/chat/completions?api-version={api_version}

    Uses the ``api-key`` header (not ``Authorization: Bearer``).
    LLM_MODEL should be the Azure deployment name.
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str,
        api_version: str = "2024-02-01",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.api_version = api_version
        self.timeout = timeout

    async def _chat(self, system: str, user: str) -> str:
        url = (
            f"{self.base_url}/openai/deployments/{self.model}"
            f"/chat/completions?api-version={self.api_version}"
        )
        headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def extract(self, report_text: str, schema: dict) -> ExtractionResponse:
        user_prompt = _build_extraction_user_prompt(report_text, schema)
        raw_text = await self._chat(_EXTRACTION_SYSTEM_PROMPT, user_prompt)
        raw = _parse_json_from_response(raw_text)
        return _normalize_extraction_response(raw, schema)

    async def suggest_fields(self, sample_text: str) -> List[dict]:
        user_prompt = f"Suggest extraction fields for this pathology report:\n\n{sample_text}"
        raw_text = await self._chat(_SUGGEST_SYSTEM_PROMPT, user_prompt)
        raw = _parse_json_from_response(raw_text)
        return raw if isinstance(raw, list) else []


# ──────────────────────────────────────────────────────────────────────────────
# Factory
# ──────────────────────────────────────────────────────────────────────────────

def get_llm_client() -> LLMClient:
    """Return the configured LLM client based on the LLM_PROVIDER environment variable.

    This is the only place the provider is resolved — callers never choose at runtime.
    """
    from core.config import settings

    provider = (settings.LLM_PROVIDER or "ollama").lower()
    logger.info(f"Initialising LLM client: provider={provider}, model={settings.LLM_MODEL}")

    if provider == "ollama":
        return OllamaClient(
            base_url=settings.LLM_BASE_URL or "http://localhost:11434",
            model=settings.LLM_MODEL or "llama3.2",
        )
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment")
        return OpenAIClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL or "gpt-4o",
        )
    elif provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment")
        return AnthropicClient(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.LLM_MODEL or "claude-3-5-sonnet-20241022",
        )
    elif provider == "generic":
        return GenericOpenAICompatibleClient(
            base_url=settings.LLM_BASE_URL or "http://localhost:8080",
            model=settings.LLM_MODEL or "default",
            api_key=settings.LLM_API_KEY or "not-needed",
        )
    elif provider == "azure":
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required for Azure provider")
        return AzureOpenAIClient(
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY,
            api_version=settings.LLM_API_VERSION,
        )
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            "Supported values: ollama, openai, anthropic, generic"
        )
