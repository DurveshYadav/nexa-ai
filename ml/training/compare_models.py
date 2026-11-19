
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from ml.features.feature_engineering import CustomerFeatureEngineer
# from ml.features.preprocessing import build_preprocessor
from ml.preprocessing.prepare_data import build_preprocessor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "customer_churn.csv"

TARGET = "churn"
TEST_SIZE = 0.20
RANDOM_STATE = 42


def build_pipeline(classifier):
    """Create a complete feature-to-prediction pipeline."""
    return Pipeline(steps=[
        ("feature_engineering", CustomerFeatureEngineer()),
        ("preprocessing", build_preprocessor()),
        ("classifier", classifier),
    ])


def main():
    df = pd.read_csv(DATASET_PATH)

    if TARGET not in df.columns:
        raise ValueError(f"Missing target column: {TARGET}")

    if df[TARGET].isna().any():
        raise ValueError("Target contains missing values")

    if not df[TARGET].isin([0, 1]).all():
        raise ValueError("Target must contain only 0 and 1")

    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    # Keep the held-out test set separate from model selection.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    models = {
        "Dummy": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5,
            min_samples_leaf=10,
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    scoring = {
        "accuracy": "accuracy",
        # "precision": "precision",
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
    }

    results = []
    pipelines = {}

    print("Training rows:", len(X_train))
    print("Held-out test rows:", len(X_test))
    print("\nRunning 5-fold cross-validation...")

    for name, classifier in models.items():
        pipeline = build_pipeline(classifier)
        pipelines[name] = pipeline

        scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cv,
            scoring=scoring,
            n_jobs=1,
            return_train_score=False,
            error_score="raise",
        )

        row = {"model": name}

        for metric in scoring:
            values = scores[f"test_{metric}"]
            row[f"{metric}_mean"] = values.mean()
            row[f"{metric}_std"] = values.std()

        results.append(row)

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        "f1_mean",
        ascending=False,
    ).reset_index(drop=True)

    print("\nCross-validation results (mean ± standard deviation):")
    display_columns = [
        "model",
        "accuracy_mean",
        "precision_mean",
        "recall_mean",
        "f1_mean",
        "f1_std",
        "roc_auc_mean",
    ]
    print(
        results_df[display_columns].to_string(
            index=False,
            float_format=lambda value: f"{value:.4f}",
        )
    )

    # Candidate selection uses CV F1, not test-set results.
    selected_name = results_df.iloc[0]["model"]
    selected_model = pipelines[selected_name]

    print(f"\nSelected candidate by CV F1: {selected_name}")

    # Fit on all training rows, then evaluate the test set once.
    selected_model.fit(X_train, y_train)
    predictions = selected_model.predict(X_test)
    probabilities = selected_model.predict_proba(X_test)[:, 1]

    print("\nHeld-out test results")
    print("Model:", selected_name)
    print("Accuracy:", accuracy_score(y_test, predictions))
    print(
        "Precision:",
        precision_score(y_test, predictions, zero_division=0),
    )
    print(
        "Recall:",
        recall_score(y_test, predictions, zero_division=0),
    )
    print("F1:", f1_score(y_test, predictions, zero_division=0))
    print("ROC-AUC:", roc_auc_score(y_test, probabilities))

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


if __name__ == "__main__":
    main()
