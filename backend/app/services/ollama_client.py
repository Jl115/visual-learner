from typing import Any, Dict

import httpx

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1"


class OllamaClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str = "",
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def generate(
        self, prompt: str, model: str | None = None, **kwargs: Any
    ) -> Dict[str, Any]:
        _model = model or self.model
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                headers=self._headers(),
                json={"model": _model, "prompt": prompt, "stream": False, **kwargs},
                timeout=120.0,
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            return data
