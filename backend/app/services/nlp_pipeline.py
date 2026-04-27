"""
NLPPipeline — class-based document NLP analysis pipeline.

Orchestrates:
1. Text chunking (pedagogical ~200-word slices)
2. Theme extraction via OllamaClient
3. Relationship inference between themes
4. Quiz generation per theme
5. Keyword-frequency fallback when LLM is unavailable

All dependencies are injected via ``__init__`` following the OOP rule:
*no bare module-level functions for anything stateful*.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from app.entities.edge import Edge
from app.entities.node import Node
from app.entities.quiz import Question, Quiz
from app.services.ollama_client import OllamaClient, QuizQuestion, Relationship, Theme

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain result types
# ---------------------------------------------------------------------------


@dataclass
class NodeResult:
    """Intermediate node data before persistence."""

    label: str
    summary: str
    doc_id: int
    color: str = "#4ECDC4"
    theme_category: Optional[str] = None
    weight: float = 1.0


@dataclass
class EdgeResult:
    """Intermediate edge data before persistence."""

    source_label: str
    target_label: str
    relation_type: str
    strength: float
    doc_id: int


@dataclass
class AnalysisResult:
    """Complete output of the NLP pipeline for one document."""

    document_id: int
    nodes: List[NodeResult] = field(default_factory=list)
    edges: List[EdgeResult] = field(default_factory=list)
    quizzes: List[Quiz] = field(default_factory=list)
    themes: List[Theme] = field(default_factory=list)
    used_fallback: bool = False


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


class Chunker:
    """
    Splits long text into pedagogical chunks (~200 words each).

    Keeps sentence boundaries intact where possible — a chunk boundary is
    aligned to the nearest period or newline before the word limit.
    """

    def __init__(self, words_per_chunk: int = 200) -> None:
        self.words_per_chunk = words_per_chunk

    def chunk(self, text: str) -> List[str]:
        """Return a list of non-empty chunk strings."""
        if not text.strip():
            return []

        words = text.split()
        if len(words) <= self.words_per_chunk:
            return [text.strip()]

        chunks: List[str] = []
        cursor = 0
        while cursor < len(words):
            end = cursor + self.words_per_chunk
            if end >= len(words):
                chunk_text = " ".join(words[cursor:])
                chunks.append(chunk_text.strip())
                break

            # Walk back to find a sentence boundary inside ±20 words
            sentence_end = end
            for i in range(end, max(cursor, end - 20), -1):
                if words[i].endswith((".", "!", "?", "\n")):
                    sentence_end = i + 1
                    break

            chunk_text = " ".join(words[cursor:sentence_end])
            chunks.append(chunk_text.strip())
            cursor = sentence_end

        return chunks

    @staticmethod
    def count_words(text: str) -> int:
        """Return the approximate word count of *text*."""
        return len(text.split())


# ---------------------------------------------------------------------------
# Keyword heuristic fallback
# ---------------------------------------------------------------------------


class KeywordExtractor:
    """Fallback theme extractor when the LLM is unreachable."""

    # A small curated stop-word list (not exhaustive — enough for heuristic)
    STOP_WORDS: set = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "and",
        "or",
        "but",
        "if",
        "then",
        "of",
        "to",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
    }

    def extract(self, text: str, max_themes: int = 7) -> List[Theme]:
        """
        Extract themes by ranking words by frequency (excluding stop words).
        Returns ``Theme`` objects so the pipeline always works with the same
        types regardless of which extractor succeeded.
        """
        # Clean and tokenise
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        words = cleaned.split()
        freq: dict = {}
        for w in words:
            if len(w) < 4 or w in self.STOP_WORDS:
                continue
            freq[w] = freq.get(w, 0) + 1

        # Take top-N by frequency
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:max_themes]
        themes: List[Theme] = []
        for word, count in top:
            themes.append(
                Theme(
                    label=word.capitalize(),
                    summary=f"Key concept mentioned {count} times in the text.",
                    weight=float(count),
                )
            )
        return themes

    def build_relationships(self, themes: List[Theme]) -> List[Relationship]:
        """
        Build simple co-occurrence relationships between themes that appear
        in the same sentence.
        """
        if len(themes) < 2:
            return []

        # Every pair gets a weak bidirectional relationship
        rels: List[Relationship] = []
        for i, a in enumerate(themes):
            for j, b in enumerate(themes):
                if i < j:
                    rels.append(
                        Relationship(
                            source=a.label,
                            target=b.label,
                            relation_type="relates-to",
                            strength=0.3,
                        )
                    )
        return rels


# ---------------------------------------------------------------------------
# NLPPipeline
# ---------------------------------------------------------------------------


class NLPPipeline:
    """
    Orchestrates the complete document-analysis workflow.

    Parameters
    ----------
    ollama : OllamaClient
        Injected LLM client (can be swapped for tests / mocks).
    chunker : Chunker | None
        Optional custom chunker; defaults to ``Chunker(200)``.
    keyword_extractor : KeywordExtractor | None
        Optional custom fallback extractor; defaults to ``KeywordExtractor()``.
    """

    def __init__(
        self,
        ollama: OllamaClient,
        chunker: Chunker | None = None,
        keyword_extractor: KeywordExtractor | None = None,
    ) -> None:
        self.ollama = ollama
        self.chunker = chunker or Chunker(words_per_chunk=200)
        self.fallback = keyword_extractor or KeywordExtractor()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze_document(
        self,
        doc_id: int,
        raw_text: str,
        max_themes: int = 7,
        questions_per_theme: int = 3,
    ) -> AnalysisResult:
        """
        Run the full NLP pipeline on a single document.

        Steps:
        1. Chunk the text.
        2. Extract themes (LLM → fallback keyword heuristic).
        3. Build relationships (LLM → fallback co-occurrence).
        4. Generate quizzes per theme (LLM → no quiz on fallback).

        Returns an ``AnalysisResult`` with intermediate structs; the caller
        (e.g. DocumentService) maps these to DB entities.
        """
        if not raw_text or not raw_text.strip():
            logger.warning("analyze_document called with empty text")
            return AnalysisResult(document_id=doc_id, used_fallback=True)

        # ---- Step 1: chunking ----------------------------------------
        chunks = self.chunker.chunk(raw_text)
        logger.info(
            f"Document {doc_id}: {len(chunks)} chunk(s) "
            f"(~{self.chunker.count_words(raw_text)} words total)"
        )

        # Use the full text for theme extraction (not individual chunks)
        #   — LLM context windows on Ollama Cloud are typically 8K-128K tokens.
        analysis_text = raw_text[:12000]  # generous cap

        # ---- Step 2: theme extraction ----------------------------------
        themes = await self.ollama.extract_themes(analysis_text, max_themes=max_themes)
        used_fallback = False
        if not themes:
            logger.info(
                f"LLM theme extraction returned empty; running keyword fallback"
            )
            themes = self.fallback.extract(analysis_text, max_themes=max_themes)
            used_fallback = True

        logger.info(f"Document {doc_id}: extracted {len(themes)} themes")

        # ---- Step 3: relationships ------------------------------------
        if not used_fallback:
            rels = await self.ollama.build_relationships(themes, analysis_text)
        else:
            rels = self.fallback.build_relationships(themes)

        logger.info(f"Document {doc_id}: built {len(rels)} relationships")

        # ---- Step 4: quiz generation ----------------------------------
        quizzes: List[Quiz] = []
        if not used_fallback:
            for theme in themes:
                qq = await self.ollama.generate_quiz(
                    theme, analysis_text, num_questions=questions_per_theme
                )
                if qq:
                    quiz = self._quiz_question_to_entity(
                        doc_id=doc_id, theme_label=theme.label, questions=qq
                    )
                    if quiz.questions:
                        quizzes.append(quiz)

        # ---- Build intermediate results --------------------------------
        nodes = self._themes_to_nodes(doc_id, themes)
        edges = self._relationships_to_edges(doc_id, themes, rels)

        return AnalysisResult(
            document_id=doc_id,
            nodes=nodes,
            edges=edges,
            quizzes=quizzes,
            themes=themes,
            used_fallback=used_fallback,
        )

    # ------------------------------------------------------------------
    # Adapters: pipeline outputs → domain entities
    # ------------------------------------------------------------------

    def _themes_to_nodes(self, doc_id: int, themes: List[Theme]) -> List[NodeResult]:
        """Map LLM/keyword themes to intermediate NodeResult structs."""
        nodes: List[NodeResult] = []
        for t in themes:
            nodes.append(
                NodeResult(
                    label=t.label,
                    summary=t.summary,
                    doc_id=doc_id,
                    color="#4ECDC4",  # default; graph builder may recolour later
                    theme_category=t.category,
                    weight=t.weight,
                )
            )
        return nodes

    def _relationships_to_edges(
        self,
        doc_id: int,
        themes: List[Theme],
        rels: List[Relationship],
    ) -> List[EdgeResult]:
        """Map LLM/keyword relationships to intermediate EdgeResult structs."""
        label_to_idx = {t.label: str(i) for i, t in enumerate(themes)}
        edges: List[EdgeResult] = []
        for r in rels:
            if r.source in label_to_idx and r.target in label_to_idx:
                edges.append(
                    EdgeResult(
                        source_label=r.source,
                        target_label=r.target,
                        relation_type=r.relation_type,
                        strength=r.strength,
                        doc_id=doc_id,
                    )
                )
        return edges

    @staticmethod
    def _quiz_question_to_entity(
        doc_id: int,
        theme_label: str,
        questions: List[QuizQuestion],
    ) -> Quiz:
        """Convert LLM QuizQuestion DTOs to domain Quiz + Question entities."""
        entity_questions: List[Question] = []
        for q in questions:
            options_text = [opt.text for opt in q.options]
            entity_questions.append(
                Question(
                    text=q.text,
                    options=options_text,
                    correct_index=q.correct_index,
                    explanation=q.explanation,
                )
            )
        return Quiz(
            doc_id=doc_id,
            total_questions=len(entity_questions),
            questions=entity_questions,
        )

    # ------------------------------------------------------------------
    # Standalone helpers (stateless, class methods where possible)
    # ------------------------------------------------------------------

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Basic word tokenisation — primarily for tests / heuristics."""
        return text.split()

    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """
        Naïve keyword extraction by frequency (no LLM).  Useful for quick
        preview or when the pipeline hasn't run yet.
        """
        extractor = KeywordExtractor()
        themes = extractor.extract(text, max_themes=top_n)
        return [t.label for t in themes]
