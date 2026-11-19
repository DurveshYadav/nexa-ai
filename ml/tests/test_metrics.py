import pytest

from ml.monitoring.metrics import PredictionMetrics


def test_metrics_count_success_and_failure():
    metrics = PredictionMetrics()

    metrics.record("success")
    metrics.record("success")
    metrics.record("failure")

    assert metrics.snapshot() == {
        "success": 2,
        "failure": 1,
        "total": 3,
    }


def test_metrics_start_at_zero():
    metrics = PredictionMetrics()

    assert metrics.snapshot() == {
        "success": 0,
        "failure": 0,
        "total": 0,
    }


def test_metrics_reject_unknown_outcomes():
    metrics = PredictionMetrics()

    with pytest.raises(ValueError):
        metrics.record("unknown")
        