
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from ml.training.model_pipeline import build_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "customer_churn.csv"

TARGET = "churn"
TEST_SIZE = 0.20
RANDOM_STATE = 42

# Replace these with your actual Phase 9 winner and parameters.
# SELECTED_MODEL_NAME = "Random Forest"
# SELECTED_MODEL_PARAMS = {
#     "n_estimators": 200,
#     "min_samples_leaf": 2,
# }
SELECTED_MODEL_NAME = "Decision Tree"

SELECTED_MODEL_PARAMS = {
    "class_weight": "balanced",
    "max_depth": 3,
    "min_samples_leaf": 10,
}

def load_dataset() -> pd.DataFrame:
    """Load the dataset and validate its target column."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    if df.empty:
        raise ValueError("Dataset is empty")

    if TARGET not in df.columns:
        raise ValueError(f"Missing target column: {TARGET}")

    if df[TARGET].isna().any():
        raise ValueError("Target contains missing values")

    if not set(df[TARGET].unique()).issubset({0, 1}):
        raise ValueError("Target must contain only 0 and 1")

    return df


def main() -> None:
    df = load_dataset()

    # Never pass the target into feature engineering or preprocessing.
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = build_pipeline(
        model_name=SELECTED_MODEL_NAME,
        params=SELECTED_MODEL_PARAMS,
    )

    print("=== NexaAI V2: Pipeline Training ===")
    print(f"Dataset rows: {len(df)}")
    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print(f"Selected model: {SELECTED_MODEL_NAME}")
    print(f"Selected parameters: {SELECTED_MODEL_PARAMS}")

    # Fits feature engineering, preprocessing, and classifier.
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("\n=== Held-out Evaluation ===")
    print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
    print(
        f"Precision: "
        f"{precision_score(y_test, predictions, zero_division=0):.4f}"
    )
    print(
        f"Recall:    "
        f"{recall_score(y_test, predictions, zero_division=0):.4f}"
    )
    print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, probabilities):.4f}")

    print("\nConfusion matrix [ [TN, FP], [FN, TP] ]:")
    print(confusion_matrix(y_test, predictions, labels=[0, 1]))

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["No churn (0)", "Churn (1)"],
            zero_division=0,
        )
    )


if __name__ == "__main__":
    main()
