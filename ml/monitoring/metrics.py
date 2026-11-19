"""Lightweight, thread-safe metrics for ML predictions."""

from collections import Counter
from threading import Lock


class PredictionMetrics:
    """Track prediction outcomes within the current application process."""

    _VALID_OUTCOMES = {"success", "failure"}

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._lock = Lock()

    def record(self, outcome: str) -> None:
        """Increment a prediction outcome counter."""
        if outcome not in self._VALID_OUTCOMES:
            raise ValueError(f"Unsupported prediction outcome: {outcome}")

        with self._lock:
            self._counts[outcome] += 1

    def snapshot(self) -> dict[str, int]:
        """Return a consistent snapshot of the counters."""
        with self._lock:
            return {
                "success": self._counts["success"],
                "failure": self._counts["failure"],
                "total": self._counts["success"] + self._counts["failure"],
            }

    def reset(self) -> None:
        """Reset counters; primarily useful in tests."""
        with self._lock:
            self._counts.clear()


prediction_metrics = PredictionMetrics()
