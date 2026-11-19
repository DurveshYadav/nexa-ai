
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ml.features.feature_engineering import CustomerFeatureEngineer
from ml.preprocessing.prepare_data import build_preprocessor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "customer_churn.csv"

TARGET = "churn"
TEST_SIZE = 0.20
RANDOM_STATE = 42


def evaluate_model(name, model, X_test, y_test):
    """Evaluate a fitted model on the held-out test set."""
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "f1": f1_score(
            y_test, predictions, zero_division=0
        ),
    }

    print(f"\n{'=' * 55}")
    print(f"Model: {name}")
    print(f"{'=' * 55}")
    print("Metrics:", metrics)

    print("\nConfusion matrix (actual rows, predicted columns):")
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

    return metrics


def main():
    # 1. Load and validate the dataset.
    df = pd.read_csv(DATASET_PATH)

    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' is missing")

    if df[TARGET].isna().any():
        raise ValueError("Target contains missing values")

    if not df[TARGET].isin([0, 1]).all():
        raise ValueError("Target must contain only 0 and 1")

    # 2. Separate features (X) from target (y).
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    # 3. Split before fitting learned preprocessing.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print("Dataset shape:", df.shape)
    print("Training rows:", len(X_train))
    print("Testing rows:", len(X_test))
    print("Target included in X:", TARGET in X.columns)

    print("\nTraining target proportions:")
    print(y_train.value_counts(normalize=True).sort_index())

    print("\nTesting target proportions:")
    print(y_test.value_counts(normalize=True).sort_index())

    # 4. Baseline: always predict the majority class.
    dummy_model = DummyClassifier(strategy="most_frequent")
    dummy_model.fit(X_train, y_train)

    dummy_metrics = evaluate_model(
        "Majority-class DummyClassifier",
        dummy_model,
        X_test,
        y_test,
    )

    # 5. Learned baseline: feature engineering + preprocessing
    #    + Logistic Regression in one pipeline.
    logistic_model = Pipeline(
        steps=[
            ("feature_engineer", CustomerFeatureEngineer()),
            ("preprocessor", build_preprocessor()),
            (
                "model",
                LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            ),
        ]
    )

    logistic_model.fit(X_train, y_train)

    logistic_metrics = evaluate_model(
        "Logistic Regression",
        logistic_model,
        X_test,
        y_test,
    )

    # 6. Compare both models on exactly the same test rows.
    comparison = pd.DataFrame(
        [dummy_metrics, logistic_metrics],
        index=["DummyClassifier", "LogisticRegression"],
    )

    print("\n=== Baseline Model Comparison ===")
    print(comparison.round(4).to_string())

    print("\nBaseline experiment completed successfully.")


if __name__ == "__main__":
    main()
