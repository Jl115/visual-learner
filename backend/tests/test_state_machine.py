"""Tests for the document state-machine and ProgressTracker."""
import pytest

from app.dto.documents import DocumentState
from app.services.state_machine import (
    ProgressTracker,
    get_next_states,
    is_terminal,
    is_valid_transition,
    stage_weight,
)


class TestStateTransitions:
    """Unit tests for raw transition-table helpers."""

    def test_valid_transitions__happy_path(self) -> None:
        """All sequential forward transitions must succeed."""
        path = [
            (DocumentState.UPLOADED, DocumentState.READING),
            (DocumentState.READING, DocumentState.PARSING),
            (DocumentState.PARSING, DocumentState.ANALYZING),
            (DocumentState.ANALYZING, DocumentState.GRAPH_BUILDING),
            (DocumentState.GRAPH_BUILDING, DocumentState.QUIZ_GENERATING),
            (DocumentState.QUIZ_GENERATING, DocumentState.COMPLETED),
        ]
        for frm, to in path:
            assert is_valid_transition(frm, to), f"{frm.value} -> {to.value}"

    def test_valid_transitions__any_to_failed(self) -> None:
        """Every non-FAILED state may transition to FAILED."""
        for state in DocumentState:
            if state == DocumentState.FAILED:
                continue
            assert is_valid_transition(state, DocumentState.FAILED)

    def test_invalid_transitions__backwards(self) -> None:
        """Reverse transitions (without retry) are illegal."""
        assert not is_valid_transition(
            DocumentState.COMPLETED, DocumentState.QUIZ_GENERATING
        )
        assert not is_valid_transition(DocumentState.READING, DocumentState.UPLOADED)

    def test_invalid_transitions__skip_ahead(self) -> None:
        """Skipping states is illegal."""
        assert not is_valid_transition(
            DocumentState.UPLOADED, DocumentState.ANALYZING
        )
        assert not is_valid_transition(
            DocumentState.PARSING, DocumentState.COMPLETED
        )

    def test_get_next_states(self) -> None:
        """Expected next-state sets."""
        assert DocumentState.PARSING in get_next_states(DocumentState.READING)
        assert DocumentState.FAILED in get_next_states(DocumentState.READING)
        assert get_next_states(DocumentState.COMPLETED) == {DocumentState.FAILED}

    def test_is_terminal(self) -> None:
        assert is_terminal(DocumentState.COMPLETED)
        assert is_terminal(DocumentState.FAILED)
        assert not is_terminal(DocumentState.ANALYZING)


class TestProgressTrackerBasics:
    """Unit tests for ProgressTracker single-state changes."""

    def test_default_state_is_uploaded(self) -> None:
        tracker = ProgressTracker()
        assert tracker.current_state == DocumentState.UPLOADED
        assert tracker.stage_progress == 0.0
        assert tracker.overall_progress == 0.0

    def test_advance_updates_state(self) -> None:
        tracker = ProgressTracker()
        tracker.advance(DocumentState.READING, stage_progress=0.5)
        assert tracker.current_state == DocumentState.READING
        assert tracker.stage_progress == 0.5

    def test_advance_rejects_illegal(self) -> None:
        tracker = ProgressTracker()
        with pytest.raises(ValueError):
            tracker.advance(DocumentState.COMPLETED)

    def test_auto_advance_moves_forward(self) -> None:
        tracker = ProgressTracker(DocumentState.UPLOADED)
        tracker.auto_advance()
        assert tracker.current_state == DocumentState.READING
        tracker.auto_advance()
        assert tracker.current_state == DocumentState.PARSING

    def test_auto_advance_does_nothing_when_terminal(self) -> None:
        tracker = ProgressTracker(DocumentState.COMPLETED)
        tracker.auto_advance()
        assert tracker.current_state == DocumentState.COMPLETED

    def test_fail_sets_message(self) -> None:
        tracker = ProgressTracker(DocumentState.READING)
        tracker.fail("PDF unreadable")
        assert tracker.current_state == DocumentState.FAILED
        assert tracker.error_msg == "PDF unreadable"

    def test_retry_from_failed(self) -> None:
        tracker = ProgressTracker(DocumentState.READING)
        tracker.fail("oops")
        tracker.retry()
        assert tracker.current_state == DocumentState.READING
        assert tracker.error_msg is None

    def test_retry_from_non_failed_raises(self) -> None:
        tracker = ProgressTracker(DocumentState.PARSING)
        with pytest.raises(RuntimeError, match="Can only retry from FAILED"):
            tracker.retry()


class TestOverallProgress:
    """Progress must be monotonic and weighted by stage."""

    def test_progress_bounds(self) -> None:
        tracker = ProgressTracker()
        tracker.advance(DocumentState.READING, stage_progress=0.5)
        p = tracker.overall_progress
        assert 0.0 <= p <= 1.0

    def test_progress_increases_through_pipeline(self) -> None:
        tracker = ProgressTracker()
        states = [
            DocumentState.READING,
            DocumentState.PARSING,
            DocumentState.ANALYZING,
            DocumentState.GRAPH_BUILDING,
            DocumentState.QUIZ_GENERATING,
            DocumentState.COMPLETED,
        ]
        prev = tracker.overall_progress
        for st in states:
            tracker.advance(st, stage_progress=0.0)
            assert tracker.overall_progress >= prev
            prev = tracker.overall_progress
        assert prev == pytest.approx(1.0, rel=1e-6)

    def test_failed_preserves_progress(self) -> None:
        tracker = ProgressTracker(DocumentState.ANALYZING, stage_progress=0.5)
        before_fail = tracker.overall_progress
        assert 0.0 < before_fail < 1.0
        tracker.fail("boom")
        assert tracker.overall_progress == pytest.approx(before_fail, rel=1e-6)

    def test_stage_weight_table_is_complete(self) -> None:
        """Every DocumentState has a defined weight."""
        for st in DocumentState:
            assert stage_weight(st) >= 0.0


class TestFullLifecycle:
    """End-to-end simulation: UPLOADED → COMPLETED."""

    def test_pipeline_simulation(self) -> None:
        """Simulate realistic stage progress through every state."""
        tracker = ProgressTracker()
        assert tracker.current_state == DocumentState.UPLOADED
        assert tracker.overall_progress == 0.0

        tracker.advance(DocumentState.READING, stage_progress=0.3)
        assert tracker.current_state == DocumentState.READING
        assert tracker.overall_progress > 0.0
        assert tracker.overall_progress < 0.20  # partial progress within READING stage

        tracker.auto_advance()  # READING → PARSING
        assert tracker.current_state == DocumentState.PARSING

        tracker.auto_advance()  # PARSING → ANALYZING
        assert tracker.current_state == DocumentState.ANALYZING

        tracker.auto_advance()  # ANALYZING → GRAPH_BUILDING
        assert tracker.current_state == DocumentState.GRAPH_BUILDING

        tracker.auto_advance()  # GRAPH_BUILDING → QUIZ_GENERATING
        assert tracker.current_state == DocumentState.QUIZ_GENERATING

        tracker.auto_advance()  # QUIZ_GENERATING → COMPLETED
        assert tracker.current_state == DocumentState.COMPLETED
        assert tracker.overall_progress == pytest.approx(1.0, rel=1e-6)

    def test_pipeline_with_retry(self) -> None:
        """Simulate failure at ANALYZING, then retry to COMPLETED."""
        tracker = ProgressTracker(DocumentState.UPLOADED)

        for _ in range(3):
            tracker.auto_advance()
        assert tracker.current_state == DocumentState.ANALYZING

        mid_progress = tracker.overall_progress
        assert 0.0 < mid_progress < 1.0

        tracker.fail("LLM timeout", stage_progress=0.4)
        assert tracker.current_state == DocumentState.FAILED
        assert tracker.error_msg == "LLM timeout"
        assert tracker.overall_progress == pytest.approx(mid_progress, rel=1e-6)

        tracker.retry()
        assert tracker.current_state == DocumentState.READING

        # complete the pipeline
        while tracker.current_state != DocumentState.COMPLETED:
            tracker.auto_advance()

        assert tracker.current_state == DocumentState.COMPLETED
        assert tracker.overall_progress == pytest.approx(1.0, rel=1e-6)


class TestCallbacks:
    """Transition hooks fire correctly."""

    def test_callback_receives_state_and_progress(self) -> None:
        calls = []

        def on_transition(_from: DocumentState, to: DocumentState, overall: float) -> None:
            calls.append((to, overall))

        tracker = ProgressTracker()
        tracker.on_transition(on_transition)
        tracker.advance(DocumentState.READING, stage_progress=0.0)

        assert len(calls) == 1
        assert calls[0][0] == DocumentState.READING
        assert 0.0 <= calls[0][1] <= 1.0
