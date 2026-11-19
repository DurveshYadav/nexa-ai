
import hashlib
import json

import joblib
import pandas as pd
import pytest

from ml.inference.model_loader import load_model
from ml.training.model_pipeline import build_pipeline


@pytest.fixture
def sample_data():
    X = pd.DataFrame(
        {
            "customer_age": [25, 40, 32, 55, 29, 48, 36, 61],
            "tenure": [2, 12, 30, 5, 18, 36, 8, 48],
            "monthly_spend": [
                30.0, 55.0, 70.0, 25.0,
                45.0, 80.0, 35.0, 90.0,
            ],
            "contract_type": [
                "monthly", "yearly", "two_year", "monthly",
                "yearly", "two_year", "monthly", "yearly",
            ],
            "support_tickets": [3, 1, 0, 4, 2, 0, 2, 1],
            "usage_frequency": [
                "low", "medium", "high", "low",
                "medium", "high", "medium", "high",
            ],
            "payment_method": [
                "card", "upi", "bank_transfer", "cash",
                "card", "upi", "cash", "bank_transfer",
            ],
        }
    )

    y = pd.Series([1, 0, 0, 1, 1, 0, 0, 1], name="churn")
    return X, y


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_artifact(tmp_path, X, y):
    version = "churn-test-v1"
    artifact_path = tmp_path / f"{version}.joblib"
    metadata_path = tmp_path / f"{version}.json"

    model = build_pipeline(
        "Logistic Regression",
        {"C": 1.0},
    )
    model.fit(X, y)

    joblib.dump(model, artifact_path)

    metadata = {
        "model_version": version,
        "target": "churn",
        "artifact_sha256": file_sha256(artifact_path),
    }
    metadata_path.write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    return model, version, artifact_path, metadata_path


def test_saved_model_predictions_match(sample_data, tmp_path):
    X, y = sample_data
    original, version, artifact_path, metadata_path = create_artifact(
        tmp_path, X, y
    )

    loaded = load_model(
        version=version,
        artifact_path=artifact_path,
        metadata_path=metadata_path,
    )

    assert (original.predict(X) == loaded.predict(X)).all()
    assert (
        original.predict_proba(X)
        == pytest.approx(loaded.predict_proba(X))
    )


def test_loader_rejects_modified_artifact(sample_data, tmp_path):
    X, y = sample_data
    _, version, artifact_path, metadata_path = create_artifact(
        tmp_path, X, y
    )

    # Change the artifact after recording its checksum.
    with artifact_path.open("ab") as file:
        file.write(b"unexpected-change")

    with pytest.raises(ValueError, match="checksum mismatch"):
        load_model(
            version=version,
            artifact_path=artifact_path,
            metadata_path=metadata_path,
        )


def test_loader_rejects_version_mismatch(sample_data, tmp_path):
    X, y = sample_data
    _, _, artifact_path, metadata_path = create_artifact(
        tmp_path, X, y
    )

    with pytest.raises(ValueError, match="version does not match"):
        load_model(
            version="churn-other-v2",
            artifact_path=artifact_path,
            metadata_path=metadata_path,
        )
