import httpx
from typing import Any, Dict

OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url

    async def generate(self, model: str, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, **kwargs},
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()
