
import hashlib
import json
from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VERSION = "churn-v1.0.0"
ARTIFACT_DIR = PROJECT_ROOT / "ml" / "artifacts"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_model(
    version: str = DEFAULT_VERSION,
    artifact_path: Path | None = None,
    metadata_path: Path | None = None,
) -> Pipeline:
    """Validate metadata and load a trusted, fitted ML pipeline."""
    # Prevent version strings from escaping the artifact directory.
    if not version or Path(version).name != version:
        raise ValueError("Invalid model version")

    artifact_path = artifact_path or (
        ARTIFACT_DIR / f"{version}.joblib"
    )
    metadata_path = metadata_path or (
        ARTIFACT_DIR / f"{version}.json"
    )

    if not artifact_path.is_file():
        raise FileNotFoundError(
            f"Model artifact not found: {artifact_path}"
        )

    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Model metadata not found: {metadata_path}"
        )

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if metadata.get("model_version") != version:
        raise ValueError("Model version does not match metadata")

    if metadata.get("target") != "churn":
        raise ValueError("Unexpected model target")

    expected_hash = metadata.get("artifact_sha256")
    if not isinstance(expected_hash, str) or not expected_hash:
        raise ValueError("Missing artifact checksum in metadata")

    actual_hash = sha256_file(artifact_path)

    if actual_hash != expected_hash:
        raise ValueError("Model artifact checksum mismatch")

    # SECURITY: joblib uses pickle-based serialization.
    # Load only artifacts from trusted sources.
    model = joblib.load(artifact_path)

    if not isinstance(model, Pipeline):
        raise TypeError("Loaded artifact is not an sklearn Pipeline")

    if not hasattr(model, "predict_proba"):
        raise TypeError("Loaded model does not support predict_proba")

    if list(model.classes_) != [0, 1]:
        raise ValueError("Model classes do not match expected [0, 1]")

    return model
