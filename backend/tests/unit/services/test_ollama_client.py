"""Unit tests for app.services.ollama_client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from app.services.ollama_client import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    ExtractRelationshipsResponse,
    GenerateQuizResponse,
    OllamaClient,
    QuizQuestion,
    Relationship,
    Theme,
)
from pydantic import ValidationError


@pytest.fixture
def client() -> OllamaClient:
    return OllamaClient(
        base_url="http://fake-ollama:11434", api_key="test-key", model="test-model"
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_defaults(self) -> None:
        oc = OllamaClient()
        assert oc.base_url == DEFAULT_BASE_URL
        assert oc.model == DEFAULT_MODEL
        assert oc.api_key == ""

    def test_custom(self, client: OllamaClient) -> None:
        assert client.base_url == "http://fake-ollama:11434"
        assert client.api_key == "test-key"
        assert client.model == "test-model"

    def test_url_stripping(self) -> None:
        oc = OllamaClient(base_url="http://host/")
        assert oc.base_url == "http://host"

    def test_headers_with_key(self, client: OllamaClient) -> None:
        assert client._headers["Authorization"] == "Bearer test-key"

    def test_headers_without_key(self) -> None:
        oc = OllamaClient()
        assert "Authorization" not in oc._headers


# ---------------------------------------------------------------------------
# Core transport
# ---------------------------------------------------------------------------


class TestGenerate:
    @pytest.mark.asyncio
    async def test_generate_happy_path(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "hello", "done": True}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            result = await client.generate("Say hello")

        assert result["response"] == "hello"
        assert result["done"] is True

    @pytest.mark.asyncio
    async def test_generate_uses_prompt(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"done": True}
        mock_resp.raise_for_status = MagicMock()
        post_mock = AsyncMock(return_value=mock_resp)

        with patch("httpx.AsyncClient.post", new=post_mock):
            await client.generate("My prompt", options={"seed": 42})

        call_args = post_mock.call_args
        payload = call_args.kwargs["json"]
        assert payload["prompt"] == "My prompt"
        assert payload["model"] == "test-model"
        assert payload["options"]["seed"] == 42


class TestChatCompletion:
    @pytest.mark.asyncio
    async def test_chat_completion_returns_content(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"themes":[]}'}}],
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            content = await client.chat_completion(
                messages=[{"role": "user", "content": "hello"}]
            )

        assert content == '{"themes":[]}'

    @pytest.mark.asyncio
    async def test_chat_completion_malformed_raises(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"unexpected": "shape"}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            with pytest.raises(RuntimeError):
                await client.chat_completion(messages=[])

    @pytest.mark.asyncio
    async def test_chat_completion_with_response_format(
        self, client: OllamaClient
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"foo":"bar"}'}}],
        }
        mock_resp.raise_for_status = MagicMock()
        post_mock = AsyncMock(return_value=mock_resp)

        with patch("httpx.AsyncClient.post", new=post_mock):
            content = await client.chat_completion(
                messages=[{"role": "user", "content": "list themes"}],
                response_format={"type": "json_object"},
            )

        payload = post_mock.call_args.kwargs["json"]
        assert payload["response_format"] == {"type": "json_object"}


# ---------------------------------------------------------------------------
# Structured helpers — extract_themes
# ---------------------------------------------------------------------------


class TestExtractThemes:
    @pytest.mark.asyncio
    async def test_extract_themes_success(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"themes":['
                            '{"label":"Quantum Mechanics","summary":"...","weight":2.5,"category":"Physics"},'
                            '{"label":"Relativity","summary":"...","weight":1.8}]'
                            "}"
                        )
                    }
                }
            ],
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            themes = await client.extract_themes(
                "Long text about physics...", max_themes=5
            )

        assert len(themes) == 2
        assert themes[0].label == "Quantum Mechanics"
        assert themes[0].category == "Physics"
        assert themes[0].weight == 2.5

    @pytest.mark.asyncio
    async def test_extract_themes_empty_on_malformed_json(
        self, client: OllamaClient
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "not json"}}],
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            themes = await client.extract_themes("some text")

        assert themes == []

    @pytest.mark.asyncio
    async def test_extract_themes_empty_on_http_error(
        self, client: OllamaClient
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "500",
                request=MagicMock(),
                response=MagicMock(),
            )
        )

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            themes = await client.extract_themes("some text")

        assert themes == []

    @pytest.mark.asyncio
    async def test_extract_themes_empty_on_validation_error(
        self, client: OllamaClient
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"themes":[{"label":"x","summary":"y","weight":-1}]}}'
                    }
                }
            ],
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            themes = await client.extract_themes("some text")

        assert themes == []


# ---------------------------------------------------------------------------
# Structured helpers — build_relationships
# ---------------------------------------------------------------------------


class TestBuildRelationships:
    @pytest.mark.asyncio
    async def test_build_relationships_success(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"relationships":['
                            '{"source":"A","target":"B","relation_type":"prerequisite-of","strength":0.9}'
                            "]}"
                        )
                    }
                }
            ],
        }
        mock_resp.raise_for_status = MagicMock()

        themes = [Theme(label="A", summary="..."), Theme(label="B", summary="...")]
        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            rels = await client.build_relationships(themes, "Some text")

        assert len(rels) == 1
        assert rels[0].relation_type == "prerequisite-of"
        assert rels[0].strength == 0.9

    @pytest.mark.asyncio
    async def test_build_relationships_empty_on_short_theme_list(
        self, client: OllamaClient
    ) -> None:
        themes = [Theme(label="A", summary="...")]
        rels = await client.build_relationships(themes, "text")
        assert rels == []


# ---------------------------------------------------------------------------
# Structured helpers — generate_quiz
# ---------------------------------------------------------------------------


class TestGenerateQuiz:
    @pytest.mark.asyncio
    async def test_generate_quiz_success(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"questions":['
                            '{"text":"Q1","options":[{"text":"Opt A"},{"text":"Opt B"}],'
                            '"correct_index":0,"explanation":"Because A is right"}'
                            "]}"
                        )
                    }
                }
            ],
        }
        mock_resp.raise_for_status = MagicMock()

        theme = Theme(label="My Theme", summary="Summary")
        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            questions = await client.generate_quiz(
                theme, "Source text", num_questions=1
            )

        assert len(questions) == 1
        assert questions[0].text == "Q1"
        assert questions[0].correct_index == 0
        assert questions[0].explanation == "Because A is right"

    @pytest.mark.asyncio
    async def test_generate_quiz_clamps_invalid_correct_index(
        self, client: OllamaClient
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"questions":['
                            '{"text":"Q","options":[{"text":"A"},{"text":"B"}],"correct_index":5}'
                            "]}"
                        )
                    }
                }
            ],
        }
        mock_resp.raise_for_status = MagicMock()

        theme = Theme(label="T", summary="S")
        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            questions = await client.generate_quiz(theme, "text", num_questions=1)

        # correct_index (5) clamped to 1 (len(options)-1)
        assert questions[0].correct_index == 1

    @pytest.mark.asyncio
    async def test_generate_quiz_empty_on_failure(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "500",
                request=MagicMock(),
                response=MagicMock(),
            )
        )

        theme = Theme(label="T", summary="S")
        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            questions = await client.generate_quiz(theme, "text")

        assert questions == []


# ---------------------------------------------------------------------------
# Utility methods
# ---------------------------------------------------------------------------


class TestHealth:
    @pytest.mark.asyncio
    async def test_health_ok_api_tags(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": [{"name": "llama3.1"}]}

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp)):
            ok, msg = await client.health()

        assert ok is True
        assert "OK" in msg

    @pytest.mark.asyncio
    async def test_health_fail_both_endpoints(self, client: OllamaClient) -> None:
        with patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(side_effect=httpx.ConnectError("refused")),
        ):
            ok, msg = await client.health()

        assert ok is False
        assert "unreachable" in msg


class TestListModels:
    @pytest.mark.asyncio
    async def test_list_models(self, client: OllamaClient) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": [{"name": "a"}, {"name": "b"}]}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp)):
            models = await client.list_models()

        assert models == ["a", "b"]


# ---------------------------------------------------------------------------
# Pydantic validation of response schemas (static, no LLM)
# ---------------------------------------------------------------------------


class TestPydanticSchemas:
    def test_theme_valid(self) -> None:
        t = Theme(label="X", summary="Y", weight=1.0)
        assert t.label == "X"

    def test_theme_invalid_weight_low(self) -> None:
        with pytest.raises(ValidationError):
            Theme(label="X", summary="Y", weight=-0.1)

    def test_theme_invalid_weight_high(self) -> None:
        with pytest.raises(ValidationError):
            Theme(label="X", summary="Y", weight=10.1)

    def test_relationship_valid(self) -> None:
        r = Relationship(
            source="A", target="B", relation_type="relates-to", strength=0.5
        )
        assert r.strength == 0.5

    def test_quiz_question_valid(self) -> None:
        q = QuizQuestion(
            text="Q", options=[{"text": "A"}, {"text": "B"}], correct_index=0
        )
        assert len(q.options) == 2
