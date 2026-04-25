import os
import httpx
import json
import asyncio
from typing import List, Dict, Any, Optional

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL, api_key: str = OLLAMA_API_KEY, model: str = DEFAULT_MODEL):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=120.0)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Simple OpenAI-compatible chat completion."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format
        try:
            resp = await self.client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Install Ollama Desktop locally or set OLLAMA_API_KEY for Ollama Cloud."
            )

    async def detect_and_set_endpoint(self):
        """Try localhost first, then fall back to configured Cloud endpoint."""
        try:
            local = httpx.AsyncClient(timeout=3.0)
            r = await local.get("http://127.0.0.1:11434/api/tags")
            if r.status_code == 200:
                self.base_url = "http://127.0.0.1:11434/v1"
                self.client = httpx.AsyncClient(base_url=self.base_url, headers={"Content-Type": "application/json"}, timeout=120.0)
                return
        except Exception:
            pass
        # Fall back to cloud or env-configured endpoint

    async def extract_themes(self, text: str, max_themes: int = 7) -> List[Dict[str, Any]]:
        """Extract structured topics + summaries from text."""
        truncated = text[:12000]  # ~12k chars for context window safety
        system_msg = (
            "You are a pedagogical AI. Given a text, extract the core educational themes. "
            "Return ONLY a JSON object with this exact shape: {"themes": [{"name": "...", "summary": "..."}]}. "
            f"Extract up to {max_themes} themes. Be concise."
        )
        user_msg = f"Analyze this text and return themes as JSON:\n\n{truncated}"

        content = await self.chat_completion(
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
            temperature=0.2,
        )
        return self._parse_json(content, "themes")

    async def build_relationships(self, themes: List[Dict], text: str) -> List[Dict[str, str]]:
        """Determine which themes relate to each other."""
        theme_names = [t["name"] for t in themes]
        system_msg = (
            "Given a list of educational topics, return a JSON object with this shape: "
            "{connections: [{source: 'Topic A', target: 'Topic B', reason: 'brief explanation'}]}. "
            "Only include meaningful pedagogical relationships (prerequisite, dependency, analogy, etc.)."
        )
        user_msg = f"Topics: {theme_names}\n\nText excerpt:\n{text[:8000]}"
        content = await self.chat_completion(
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
            temperature=0.2,
        )
        return self._parse_json(content, "connections")

    async def generate_quiz(self, theme_name: str, theme_summary: str, text: str) -> List[Dict[str, Any]]:
        """Generate multiple-choice questions for a topic."""
        system_msg = (
            "You are a quiz generator. Return ONLY a JSON object with this exact shape: "
            "{questions: [{question: '...', options: ['A','B','C','D'], correct_index: 0}]}. "
            "Generate 3 well-crafted multiple choice questions. Correct index is 0-based."
        )
        user_msg = f"Topic: {theme_name}\nSummary: {theme_summary}\n\nText:\n{text[:6000]}"
        content = await self.chat_completion(
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
            temperature=0.6,
        )
        return self._parse_json(content, "questions")

    async def chunk_entities(self, text: str) -> List[str]:
        """Split text into pedagogical chunks."""
        system_msg = (
            "Split the following text into concise pedagogical chunks (~200 words each). "
            "Return ONLY a JSON object: {chunks: ['...', '...']}."
        )
        content = await self.chat_completion(
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": text[:10000]}],
            temperature=0.2,
            max_tokens=2048,
        )
        return self._parse_json(content, "chunks")

    @staticmethod
    def _parse_json(raw: str, key: str) -> Any:
        """Robust JSON extraction from markdown-wrapped LLM responses."""
        text = raw.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            obj = json.loads(text)
            return obj.get(key, [])
        except json.JSONDecodeError:
            # Last resort: try to find the first JSON object in the text
            try:
                start = text.index("{")
                end = text.rindex("}") + 1
                obj = json.loads(text[start:end])
                return obj.get(key, [])
            except (ValueError, json.JSONDecodeError):
                return []
