"""
OllamaClient — typed OpenAI-compatible client for Ollama Cloud.

All LLM calls return **JSON-only** responses that are validated by Pydantic
before being consumed downstream.  The client supports:

* synchronous and async chat completion
* single-turn generate (legacy Ollama /api/generate)
* structured-output extraction: themes, relationships, quiz questions
* health-check / model-list probes
* transparent fallback to keyword heuristics when the LLM is unreachable

Design principle: every public method is a class method or instance method —
no module-level state, no bare functions.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://ollama.com/v1"  # Ollama Cloud OpenAI-compatible
DEFAULT_MODEL = "llama3.1"
CHUNK_SIZE_WORDS = 200


# ---------------------------------------------------------------------------
# Pydantic response schemas — enforced before any downstream consumption
# ---------------------------------------------------------------------------


class Theme(BaseModel):
    """A pedagogical theme extracted from document text."""

    label: str = Field(..., min_length=1, max_length=120)
    summary: str = Field(..., max_length=500)
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    category: Optional[str] = None

    model_config = {"extra": "forbid"}


class Relationship(BaseModel):
    """A directed pedagogical connection between two themes."""

    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    relation_type: str = Field(..., min_length=1)
    strength: float = Field(default=0.5, ge=0.0, le=1.0)

    model_config = {"extra": "forbid"}


class QuizOption(BaseModel):
    """One multiple-choice option for a quiz question."""

    text: str = Field(..., min_length=1)


class QuizQuestion(BaseModel):
    """A single multiple-choice question derived from a theme."""

    text: str = Field(..., min_length=1)
    options: List[QuizOption] = Field(default_factory=list, min_length=2, max_length=6)
    correct_index: int = Field(..., ge=0)
    explanation: Optional[str] = None

    model_config = {"extra": "forbid"}


class ExtractThemesResponse(BaseModel):
    """Wrapper so the LLM can return a top-level JSON object with a list."""

    themes: List[Theme] = Field(default_factory=list, max_length=50)


class ExtractRelationshipsResponse(BaseModel):
    relationships: List[Relationship] = Field(default_factory=list, max_length=200)


class GenerateQuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(default_factory=list, max_length=50)


# ---------------------------------------------------------------------------
# OllamaClient
# ---------------------------------------------------------------------------


class OllamaClient:
    """
    Async-first HTTP client for Ollama / Ollama Cloud.

    Parameters
    ----------
    base_url : str
        Root URL of the Ollama endpoint (default: ``https://ollama.com/v1``).
    api_key : str | None
        Optional API key for authenticated endpoints.
    model : str
        Default model tag (e.g. ``llama3.1``).
    timeout : float
        Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str = "",
        model: str = DEFAULT_MODEL,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

        # Pre-built headers (immutable after init)
        self._headers: Dict[str, str] = {}
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"

    # ------------------------------------------------------------------
    # Core transport
    # ------------------------------------------------------------------

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        response_format: Dict[str, Any] | None = None,
        **extra: Any,
    ) -> str:
        """
        OpenAI-compatible ``/v1/chat/completions`` endpoint.

        Returns the *content* of the first choice — raw string that the
        caller is expected to parse as JSON when ``response_format`` hints JSON.
        """
        _model = model or self.model
        payload: Dict[str, Any] = {
            "model": _model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            **extra,
        }
        if response_format is not None:
            payload["response_format"] = response_format

        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=self._headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            logger.warning(f"Malformed chat response from Ollama: {data}")
            raise RuntimeError(f"Unexpected response shape: {exc}") from exc

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Legacy Ollama native ``/api/generate`` endpoint.
        Returns the full JSON response dict so callers can inspect ``response``
        and metadata themselves.
        """
        _model = model or self.model
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                headers=self._headers,
                json={"model": _model, "prompt": prompt, "stream": False, **kwargs},
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Structured helpers
    # ------------------------------------------------------------------

    async def _structured_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """Small helper: sends a system + user message pair, returns raw content."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
        )

    async def extract_themes(
        self,
        text: str,
        max_themes: int = 7,
        model: str | None = None,
    ) -> List[Theme]:
        """
        Ask the LLM to extract up to *max_themes* pedagogical themes from *text*.

        The prompt explicitly demands JSON with a single ``themes`` array.
        If validation fails or the LLM is unreachable, returns an empty list
        so callers can fall back to keyword heuristics.
        """
        system_prompt = (
            "You are an educational-content analyst. "
            "Your job is to extract pedagogical themes from the text. "
            "Reply ONLY with valid JSON conforming to this shape:\n"
            '{"themes":[{"label":"...","summary":"...","weight":1.0,"category":"..."}]}'
        )
        user_prompt = (
            f"Extract up to {max_themes} key themes from the following text.\n\n"
            f"TEXT:\n{text[:8000]}\n\n"
            "Respond with JSON only. No prose, no markdown code fences."
        )

        try:
            raw = await self._structured_chat(system_prompt, user_prompt, model=model)
            parsed = json.loads(raw)
            validated = ExtractThemesResponse.model_validate(parsed)
            return validated.themes
        except (json.JSONDecodeError, ValidationError, httpx.HTTPError, RuntimeError) as exc:
            logger.warning(f"Theme extraction failed: {exc}")
            return []

    async def build_relationships(
        self,
        themes: List[Theme],
        text: str,
        model: str | None = None,
    ) -> List[Relationship]:
        """
        Ask the LLM to infer pedagogical relationships between the given themes.

        Returns an empty list on any failure so the graph builder can fall back
        to co-occurrence heuristics.
        """
        if len(themes) < 2:
            return []

        theme_labels = ", ".join(t.label for t in themes)
        system_prompt = (
            "You are a knowledge-graph builder. "
            "Given a set of themes and the source text, infer directed pedagogical "
            "relationships (e.g. 'prerequisite-of', 'relates-to', 'example-of').\n"
            "Reply ONLY with valid JSON conforming to this shape:\n"
            '{"relationships":['
            '{"source":"...","target":"...","relation_type":"...","strength":0.8}'
            ']}'
        )
        user_prompt = (
            f"Themes: {theme_labels}\n\n"
            f"Source text:\n{text[:6000]}\n\n"
            "Respond with JSON only. No prose, no markdown code fences."
        )

        try:
            raw = await self._structured_chat(system_prompt, user_prompt, model=model)
            parsed = json.loads(raw)
            validated = ExtractRelationshipsResponse.model_validate(parsed)
            return validated.relationships
        except (json.JSONDecodeError, ValidationError, httpx.HTTPError, RuntimeError) as exc:
            logger.warning(f"Relationship extraction failed: {exc}")
            return []

    async def generate_quiz(
        self,
        theme: Theme,
        text: str,
        num_questions: int = 5,
        model: str | None = None,
    ) -> List[QuizQuestion]:
        """
        Ask the LLM to generate multiple-choice questions based on a single theme.

        Returns an empty list on failure so the quiz pipeline can fall back to
        template-based questions.
        """
        system_prompt = (
            "You are an educational quiz designer. "
            "Generate multiple-choice questions that test understanding of the given theme. "
            "Reply ONLY with valid JSON conforming to this shape:\n"
            '{"questions":['
            '{"text":"...","options":[{"text":"..."},{"text":"..."}],'
            '"correct_index":0,"explanation":"..."}'
            ']}'
        )
        user_prompt = (
            f"Theme: {theme.label}\n"
            f"Summary: {theme.summary}\n\n"
            f"Source text:\n{text[:6000]}\n\n"
            f"Generate exactly {num_questions} questions. "
            "Respond with JSON only. No prose, no markdown code fences."
        )

        try:
            raw = await self._structured_chat(system_prompt, user_prompt, model=model)
            parsed = json.loads(raw)
            validated = GenerateQuizResponse.model_validate(parsed)
            # Extra safety clamp correct_index
            for q in validated.questions:
                if q.options and q.correct_index >= len(q.options):
                    q.correct_index = len(q.options) - 1
            return validated.questions
        except (json.JSONDecodeError, ValidationError, httpx.HTTPError, RuntimeError) as exc:
            logger.warning(f"Quiz generation failed: {exc}")
            return []

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    async def health(self) -> Tuple[bool, str]:
        """
        Probe the Ollama endpoint for reachability.

        Returns ``(True, model_name)`` on success, ``(False, error_msg)`` otherwise.
        """
        try:
            # Try the legacy tags endpoint first (works on local Ollama)
            url = f"{self.base_url}/api/tags"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self._headers)
                if resp.status_code == 200:
                    data = resp.json()
                    models = data.get("models", [])
                    names = [m.get("name", "unknown") for m in models[:3]]
                    return True, f"OK — models: {', '.join(names)}"
        except Exception as exc:
            logger.debug(f"Health check via /api/tags failed: {exc}")

        try:
            # Fallback: Ollama Cloud uses /models
            url = f"{self.base_url}/models"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self._headers)
                if resp.status_code == 200:
                    return True, "OK — Ollama Cloud reachable"
        except Exception as exc:
            logger.debug(f"Health check via /models failed: {exc}")

        return False, f"Ollama unreachable at {self.base_url}"

    async def list_models(self) -> List[str]:
        """Return a list of available model tags from the Ollama endpoint."""
        try:
            url = f"{self.base_url}/api/tags"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=self._headers)
                resp.raise_for_status()
                data = resp.json()
                return [m["name"] for m in data.get("models", []) if "name" in m]
        except Exception as exc:
            logger.warning(f"Could not list models: {exc}")
            return []
