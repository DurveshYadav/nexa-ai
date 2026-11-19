import pytest

from ml.monitoring.metrics import PredictionMetrics


def test_records_success_and_failure():
    metrics = PredictionMetrics()

    metrics.record("success")
    metrics.record("success")
    metrics.record("failure")

    assert metrics.snapshot() == {
        "success": 2,
        "failure": 1,
        "total": 3,
    }


def test_rejects_unknown_outcome():
    metrics = PredictionMetrics()

    with pytest.raises(ValueError, match="Unsupported prediction outcome"):
        metrics.record("unknown")


def test_reset_clears_counters():
    metrics = PredictionMetrics()
    metrics.record("success")

    metrics.reset()

    assert metrics.snapshot() == {
        "success": 0,
        "failure": 0,
        "total": 0,
    }
