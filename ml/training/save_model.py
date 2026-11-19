
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn

from ml.training.model_pipeline import build_pipeline
from ml.training.train_pipeline import (
    SELECTED_MODEL_NAME,
    SELECTED_MODEL_PARAMS,
    load_dataset,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = PROJECT_ROOT / "ml" / "artifacts"

MODEL_VERSION = "churn-v1.0.0"
MODEL_PATH = ARTIFACT_DIR / f"{MODEL_VERSION}.joblib"
METADATA_PATH = ARTIFACT_DIR / f"{MODEL_VERSION}.json"


def sha256_file(path: Path) -> str:
    """Calculate the SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_dataset()

    X = df.drop(columns=["churn"])
    y = df["churn"].astype(int)

    model = build_pipeline(
        model_name=SELECTED_MODEL_NAME,
        params=SELECTED_MODEL_PARAMS,
    )

    print("=== NexaAI V2: Final Model Training ===")
    print(f"Dataset rows: {len(df)}")
    print(f"Model: {SELECTED_MODEL_NAME}")
    print(f"Parameters: {SELECTED_MODEL_PARAMS}")

    # Fit the entire pipeline on the complete dataset.
    model.fit(X, y)

    # Save the fitted pipeline.
    joblib.dump(model, MODEL_PATH)

    # Calculate a checksum so the loader can detect file changes.
    artifact_hash = sha256_file(MODEL_PATH)

    metadata = {
        "model_name": SELECTED_MODEL_NAME,
        "model_version": MODEL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": "churn",
        "classes": [int(value) for value in model.classes_],
        "training_rows": int(len(X)),
        "feature_columns": list(X.columns),
        "model_parameters": SELECTED_MODEL_PARAMS,
        "dataset_sha256": sha256_file(
            PROJECT_ROOT / "ml" / "data" / "customer_churn.csv"
        ),
        "artifact_sha256": artifact_hash,
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "scikit_learn_version": sklearn.__version__,
        "joblib_version": joblib.__version__,
    }

    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print("\nModel artifact saved:")
    print(MODEL_PATH)

    print("\nMetadata saved:")
    print(METADATA_PATH)

    print(f"\nArtifact SHA-256: {artifact_hash}")
    print("\nTraining and serialization completed.")


if __name__ == "__main__":
    main()
