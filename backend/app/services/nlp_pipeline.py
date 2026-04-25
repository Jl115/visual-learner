import asyncio
from typing import List, Dict, Any
from app.services.ollama_client import OllamaClient

async def analyze_document(doc_id: str, raw_text: str) -> Dict[str, Any]:
    """Full async NLP pipeline: themes -> relationships -> quizzes."""
    client = OllamaClient()
    await client.detect_and_set_endpoint()  # prefers local Ollama if running

    # 1. Extract themes
    themes = await client.extract_themes(raw_text)
    if not themes:
        # Ultimate fallback: simple keyword-frequency topics
        themes = _fallback_themes(raw_text)

    # 2. Build relationships
    connections = await client.build_relationships(themes, raw_text)

    # 3. Generate quizzes for each theme concurrently
    quizzes: Dict[str, List[Dict[str, Any]]] = {}
    async def gen_quiz(theme: Dict):
        qs = await client.generate_quiz(theme["name"], theme.get("summary", ""), raw_text)
        return theme["name"], qs

    quiz_results = await asyncio.gather(*[gen_quiz(t) for t in themes])
    for theme_name, qs in quiz_results:
        quizzes[theme_name] = qs

    return {
        "themes": themes,
        "connections": connections,
        "quizzes": quizzes,
    }

def _fallback_themes(text: str) -> List[Dict[str, Any]]:
    """Naive fallback if LLM fails completely."""
    # Simple frequency-based paragraph headers
    paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 40]
    themes = []
    for i, para in enumerate(paragraphs[:7]):
        first_sentence = para.split(".")[0] if "." in para else para[:60]
        themes.append({
            "name": first_sentence[:50],
            "summary": para[:200],
        })
    return themes
