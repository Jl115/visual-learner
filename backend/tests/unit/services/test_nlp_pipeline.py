"""Unit tests for app.services.nlp_pipeline."""

from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from app.services.nlp_pipeline import (
    AnalysisResult,
    Chunker,
    EdgeResult,
    KeywordExtractor,
    NLPPipeline,
    NodeResult,
)
from app.services.ollama_client import OllamaClient, QuizQuestion, Relationship, Theme

# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


class TestChunker:
    def test_empty_text(self) -> None:
        c = Chunker()
        assert c.chunk("") == []

    def test_short_text_single_chunk(self) -> None:
        c = Chunker(words_per_chunk=200)
        text = "This is a short sentence."
        assert c.chunk(text) == [text]

    def test_long_text_multiple_chunks(self) -> None:
        c = Chunker(words_per_chunk=5)
        text = "One two three four five six seven eight nine ten."
        chunks = c.chunk(text)
        assert len(chunks) > 1
        # First chunk should include sentence boundary (ends with period)
        assert chunks[0].endswith("five.") or "five" in chunks[0]

    def test_count_words(self) -> None:
        c = Chunker()
        assert c.count_words("hello world foo") == 3

    def test_custom_chunk_size(self) -> None:
        c = Chunker(words_per_chunk=3)
        text = "A B C D E F."
        chunks = c.chunk(text)
        assert len(chunks) >= 2


# ---------------------------------------------------------------------------
# KeywordExtractor
# ---------------------------------------------------------------------------


class TestKeywordExtractor:
    def test_extract_basic(self) -> None:
        k = KeywordExtractor()
        text = "Machine learning is amazing. Machine learning helps solve problems."
        themes = k.extract(text, max_themes=2)
        assert len(themes) == 2
        labels = [t.label for t in themes]
        assert "Machine" in labels[0] or "learning" in labels[0].lower()

    def test_extract_respects_max_themes(self) -> None:
        k = KeywordExtractor()
        text = "Word1 Word2 Word3 Word4 Word5 Word6."
        themes = k.extract(text, max_themes=2)
        assert len(themes) <= 2

    def test_build_relationships_empty(self) -> None:
        k = KeywordExtractor()
        rels = k.build_relationships([])
        assert rels == []

    def test_build_relationships_pairs(self) -> None:
        k = KeywordExtractor()
        themes = [Theme(label="A", summary="..."), Theme(label="B", summary="...")]
        rels = k.build_relationships(themes)
        assert len(rels) == 1
        assert rels[0].relation_type == "relates-to"
        assert rels[0].strength == 0.3

    def test_ignores_stop_words(self) -> None:
        k = KeywordExtractor()
        text = "the and is are was were be been being"
        themes = k.extract(text, max_themes=10)
        assert len(themes) == 0


# ---------------------------------------------------------------------------
# NLPPipeline construction
# ---------------------------------------------------------------------------


class TestNLPPipelineConstruction:
    def test_default_construction(self) -> None:
        ollama = MagicMock(spec=OllamaClient)
        pipeline = NLPPipeline(ollama=ollama)
        assert pipeline.ollama is ollama
        assert isinstance(pipeline.chunker, Chunker)
        assert isinstance(pipeline.fallback, KeywordExtractor)

    def test_custom_chunker(self) -> None:
        ollama = MagicMock(spec=OllamaClient)
        custom_chunker = Chunker(words_per_chunk=50)
        pipeline = NLPPipeline(ollama=ollama, chunker=custom_chunker)
        assert pipeline.chunker is custom_chunker

    def test_injected_dependencies(self) -> None:
        ollama = MagicMock(spec=OllamaClient)
        chunker = Chunker(words_per_chunk=100)
        fallback = KeywordExtractor()
        pipeline = NLPPipeline(
            ollama=ollama, chunker=chunker, keyword_extractor=fallback
        )
        assert pipeline.ollama is ollama
        assert pipeline.chunker is chunker
        assert pipeline.fallback is fallback


# ---------------------------------------------------------------------------
# NLPPipeline.analyze_document — happy path
# ---------------------------------------------------------------------------


class TestAnalyzeDocumentHappyPath:
    @pytest.mark.asyncio
    async def test_full_pipeline_llm_success(self) -> None:
        """When LLM returns themes, relationships, and quizzes — pipeline produces a full result."""
        ollama = MagicMock(spec=OllamaClient)
        ollama.extract_themes = AsyncMock(
            return_value=[
                Theme(label="Theme A", summary="Summary A", weight=1.5),
                Theme(label="Theme B", summary="Summary B", weight=2.0),
            ]
        )
        ollama.build_relationships = AsyncMock(
            return_value=[
                Relationship(
                    source="Theme A",
                    target="Theme B",
                    relation_type="prerequisite-of",
                    strength=0.8,
                )
            ]
        )
        ollama.generate_quiz = AsyncMock(
            return_value=[
                QuizQuestion(
                    text="Q1",
                    options=[{"text": "A"}, {"text": "B"}],
                    correct_index=0,
                    explanation="Because A",
                )
            ]
        )

        pipeline = NLPPipeline(ollama=ollama)
        result = await pipeline.analyze_document(
            doc_id=1,
            raw_text="Some long text about things.",
            max_themes=2,
            questions_per_theme=1,
        )

        assert isinstance(result, AnalysisResult)
        assert result.document_id == 1
        assert len(result.nodes) == 2
        assert len(result.edges) == 1
        # generate_quiz is called once per theme → 2 quizzes total
        assert len(result.quizzes) == 2
        assert result.used_fallback is False
        assert len(result.themes) == 2

        # Verify node values
        node_labels = {n.label for n in result.nodes}
        assert node_labels == {"Theme A", "Theme B"}

    @pytest.mark.asyncio
    async def test_no_quizzes_when_no_themes(self) -> None:
        ollama = MagicMock(spec=OllamaClient)
        ollama.extract_themes = AsyncMock(return_value=[])

        pipeline = NLPPipeline(ollama=ollama)
        result = await pipeline.analyze_document(doc_id=2, raw_text="Short text here")

        # Fallback keyword extractor runs
        assert result.used_fallback is True
        assert len(result.nodes) > 0
        assert result.quizzes == []

    @pytest.mark.asyncio
    async def test_empty_text_returns_empty_result(self) -> None:
        ollama = MagicMock(spec=OllamaClient)
        pipeline = NLPPipeline(ollama=ollama)
        result = await pipeline.analyze_document(doc_id=3, raw_text="")

        assert result.document_id == 3
        assert result.nodes == []
        assert result.used_fallback is True  # fallback runs
        # Keyword fallback may still produce nodes, but no quizzes from LLM
        assert result.quizzes == []
        ollama.extract_themes.assert_not_called()


# ---------------------------------------------------------------------------
# NLPPipeline.analyze_document — fallback path
# ---------------------------------------------------------------------------


class TestAnalyzeDocumentFallback:
    @pytest.mark.asyncio
    async def test_llm_empty_triggers_keyword_fallback(self) -> None:
        ollama = MagicMock(spec=OllamaClient)
        ollama.extract_themes = AsyncMock(return_value=[])  # LLM returns nothing

        pipeline = NLPPipeline(ollama=ollama)
        result = await pipeline.analyze_document(
            doc_id=4,
            raw_text="Machine learning is important. Machine learning is fascinating.",
        )

        assert result.used_fallback is True
        assert len(result.nodes) > 0  # keyword extractor produced themes
        assert len(result.themes) > 0
        # No edge from fallback for short text


# ---------------------------------------------------------------------------
# Internal helpers (_themes_to_nodes, _relationships_to_edges, etc.)
# ---------------------------------------------------------------------------


class TestInternalHelpers:
    def test_themes_to_nodes(self) -> None:
        pipeline = NLPPipeline(ollama=MagicMock(spec=OllamaClient))
        themes = [Theme(label="X", summary="S", weight=3.0, category="Test")]
        nodes = pipeline._themes_to_nodes(doc_id=1, themes=themes)
        assert len(nodes) == 1
        assert nodes[0].label == "X"
        assert nodes[0].summary == "S"
        assert nodes[0].weight == 3.0
        assert nodes[0].theme_category == "Test"

    def test_relationships_to_edges(self) -> None:
        pipeline = NLPPipeline(ollama=MagicMock(spec=OllamaClient))
        themes = [Theme(label="A", summary="S"), Theme(label="B", summary="S")]
        rels = [
            Relationship(
                source="A", target="B", relation_type="relates-to", strength=0.5
            )
        ]
        edges = pipeline._relationships_to_edges(doc_id=1, themes=themes, rels=rels)
        assert len(edges) == 1
        assert edges[0].source_label == "A"
        assert edges[0].target_label == "B"
        assert edges[0].strength == 0.5

    def test_relationships_to_edges_ignores_unknown(self) -> None:
        pipeline = NLPPipeline(ollama=MagicMock(spec=OllamaClient))
        themes = [Theme(label="A", summary="S")]
        rels = [
            Relationship(
                source="A", target="Z", relation_type="relates-to", strength=0.5
            )
        ]
        edges = pipeline._relationships_to_edges(doc_id=1, themes=themes, rels=rels)
        assert len(edges) == 0  # Z not in themes → dropped

    @pytest.mark.asyncio
    async def test_quiz_question_to_entity(self) -> None:
        pipeline = NLPPipeline(ollama=MagicMock(spec=OllamaClient))
        qq = [
            QuizQuestion(
                text="Q1",
                options=[{"text": "A"}, {"text": "B"}],
                correct_index=0,
                explanation="Because A",
            )
        ]
        quiz = NLPPipeline._quiz_question_to_entity(
            doc_id=1, theme_label="Test", questions=qq
        )
        assert quiz.doc_id == 1
        assert len(quiz.questions) == 1
        assert quiz.questions[0].text == "Q1"
        assert quiz.questions[0].options == ["A", "B"]
        assert quiz.questions[0].correct_index == 0
        assert quiz.questions[0].explanation == "Because A"


# ---------------------------------------------------------------------------
# Stateless helpers
# ---------------------------------------------------------------------------


class TestStatelessHelpers:
    def test_tokenize(self) -> None:
        pipeline = NLPPipeline(ollama=MagicMock(spec=OllamaClient))
        tokens = pipeline.tokenize("hello world")
        assert tokens == ["hello", "world"]

    def test_extract_keywords(self) -> None:
        pipeline = NLPPipeline(ollama=MagicMock(spec=OllamaClient))
        keywords = pipeline.extract_keywords(
            "Machine learning helps with machine learning problems.", top_n=2
        )
        assert len(keywords) <= 2
        assert all(isinstance(k, str) for k in keywords)
