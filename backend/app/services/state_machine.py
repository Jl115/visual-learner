"""Document lifecycle state machine with transition rules and progress tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from app.dto.documents import DocumentState


# ─── transition table ──────────────────────────────────────────────
_TRANSITIONS: dict[DocumentState, set[DocumentState]] = {
    DocumentState.UPLOADED: {DocumentState.READING, DocumentState.FAILED},
    DocumentState.READING: {DocumentState.PARSING, DocumentState.FAILED},
    DocumentState.PARSING: {DocumentState.ANALYZING, DocumentState.FAILED},
    DocumentState.ANALYZING: {DocumentState.GRAPH_BUILDING, DocumentState.FAILED},
    DocumentState.GRAPH_BUILDING: {DocumentState.QUIZ_GENERATING, DocumentState.FAILED},
    DocumentState.QUIZ_GENERATING: {DocumentState.COMPLETED, DocumentState.FAILED},
    DocumentState.COMPLETED: {DocumentState.FAILED},
    DocumentState.FAILED: {DocumentState.READING},  # retry resets pipeline
}


def is_valid_transition(from_state: DocumentState, to_state: DocumentState) -> bool:
    """Return True if *to_state* is reachable from *from_state*."""
    return to_state in _TRANSITIONS.get(from_state, set())


def get_next_states(state: DocumentState) -> set[DocumentState]:
    """Return all valid next states from *state*."""
    return set(_TRANSITIONS.get(state, set()))


def is_terminal(state: DocumentState) -> bool:
    """COMPLETED and FAILED are terminal in the normal flow."""
    return state in {DocumentState.COMPLETED, DocumentState.FAILED}


# ─── state weights for overall progress ──────────────────────────
_STATE_WEIGHTS: dict[DocumentState, float] = {
    DocumentState.UPLOADED: 0.0,
    DocumentState.READING: 0.15,
    DocumentState.PARSING: 0.30,
    DocumentState.ANALYZING: 0.50,
    DocumentState.GRAPH_BUILDING: 0.70,
    DocumentState.QUIZ_GENERATING: 0.85,
    DocumentState.COMPLETED: 1.0,
    DocumentState.FAILED: 0.0,
}

_PROGRESSION_STATES: list[DocumentState] = [
    DocumentState.UPLOADED,
    DocumentState.READING,
    DocumentState.PARSING,
    DocumentState.ANALYZING,
    DocumentState.GRAPH_BUILDING,
    DocumentState.QUIZ_GENERATING,
    DocumentState.COMPLETED,
]


def _state_index(state: DocumentState) -> int:
    try:
        return _PROGRESSION_STATES.index(state)
    except ValueError:
        return 0  # FAILED or unknown


# ─── callbacks ─────────────────────────────────────────────────────
StateCallback = Callable[[DocumentState, DocumentState, float], None]


@dataclass
class ProgressTracker:
    """Tracks document lifecycle with stage-level and overall progress.

    Usage
    =====
    >>> tracker = ProgressTracker()
    >>> tracker.advance(DocumentState.READING, stage_progress=0.5)
    >>> tracker.current_state
    <DocumentState.READING: 'reading'>
    >>> tracker.overall_progress
    0.075  # 0% base + 0.5 * 15% weight
    """

    current_state: DocumentState = DocumentState.UPLOADED
    stage_progress: float = 0.0  # 0.0-1.0 within the *current* stage
    error_msg: Optional[str] = None
    _callbacks: list[StateCallback] = field(default_factory=list, repr=False)
    _pre_failure_state: Optional[DocumentState] = field(default=None, repr=False)
    _failure_progress: float = field(default=0.0, repr=False)

    # ─── public API ──────────────────────────────────────────────

    def advance(
        self,
        to_state: DocumentState,
        *,
        stage_progress: float = 0.0,
        error_msg: Optional[str] = None,
    ) -> None:
        """Request a state transition.

        Raises ``ValueError`` if the transition is illegal.
        """
        if not is_valid_transition(self.current_state, to_state):
            raise ValueError(
                f"Illegal transition {self.current_state.value} -> {to_state.value}"
            )

        from_state = self.current_state

        # Capture pre-failure progress BEFORE mutating state
        if to_state == DocumentState.FAILED:
            self._pre_failure_state = from_state
            self._failure_progress = self.overall_progress

        self.current_state = to_state
        self.stage_progress = max(0.0, min(1.0, stage_progress))

        if to_state == DocumentState.FAILED and error_msg:
            self.error_msg = error_msg
        elif to_state != DocumentState.FAILED:
            self.error_msg = None

        self._notify(from_state, to_state)

    def auto_advance(self, stage_progress: float = 1.0) -> None:
        """Move to the next linear state (e.g. READING → PARSING)."""
        if is_terminal(self.current_state):
            return  # already terminal
        nxt = get_next_states(self.current_state)
        fwd = [s for s in nxt if s != DocumentState.FAILED]
        if not fwd:
            return  # no forward states
        self.advance(fwd[0], stage_progress=stage_progress)

    def fail(self, message: str, *, stage_progress: float = 0.0) -> None:
        """Convenience: transition to FAILED with an error message."""
        self.advance(
            DocumentState.FAILED, stage_progress=stage_progress, error_msg=message
        )

    def retry(self) -> None:
        """Reset from FAILED back to READING to restart the pipeline."""
        if self.current_state != DocumentState.FAILED:
            raise RuntimeError("Can only retry from FAILED state")
        self._pre_failure_state = None
        self._failure_progress = 0.0
        self.advance(DocumentState.READING, stage_progress=0.0)

    def on_transition(self, callback: StateCallback) -> StateCallback:
        """Register a callback invoked on every successful transition.

        Returns the callback so it can be used as a decorator.
        """
        self._callbacks.append(callback)
        return callback

    # ─── progress calculations ───────────────────────────────────

    @property
    def overall_progress(self) -> float:
        """Weighted 0.0-1.0 across the full pipeline."""
        if self.current_state == DocumentState.FAILED:
            return self._failure_progress
        base = _STATE_WEIGHTS.get(self.current_state, 0.0)
        idx = _state_index(self.current_state)
        if idx < len(_PROGRESSION_STATES) - 1:
            next_state = _PROGRESSION_STATES[idx + 1]
            span = _STATE_WEIGHTS[next_state] - base
            return base + self.stage_progress * span
        return base  # COMPLETED

    # ─── internal helpers ────────────────────────────────────────

    def _notify(self, from_state: DocumentState, to_state: DocumentState) -> None:
        ov = self.overall_progress
        for cb in self._callbacks:
            try:
                cb(from_state, to_state, ov)
            except Exception:  # pragma: no cover
                pass


# ─── shared helpers for services ─────────────────────────────────

def default_progress_callback(
    on_change: Optional[Callable[[DocumentState, float], None]] = None,
) -> StateCallback:
    """Factory returning a callback that forwards *(state, overall)* pairs."""
    def _cb(_from: DocumentState, to: DocumentState, overall: float) -> None:
        if on_change is not None:
            on_change(to, overall)
    return _cb


def stage_weight(state: DocumentState) -> float:
    """Return the base weight of a state (used by overall_progress)."""
    return _STATE_WEIGHTS.get(state, 0.0)
