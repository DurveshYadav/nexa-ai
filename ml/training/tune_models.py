
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from ml.features.feature_engineering import CustomerFeatureEngineer
# from ml.features.preprocessing import build_preprocessor
from ml.preprocessing.prepare_data import build_preprocessor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "customer_churn.csv"
RESULTS_PATH = PROJECT_ROOT / "ml" / "training" / "tuning_results.csv"

TARGET = "churn"
TEST_SIZE = 0.20
RANDOM_STATE = 42
CV_FOLDS = 5


def build_pipeline() -> Pipeline:
    """Build the complete, leakage-aware ML pipeline."""
    return Pipeline(
        steps=[
            ("feature_engineering", CustomerFeatureEngineer()),
            ("preprocessing", build_preprocessor()),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


def build_parameter_grid() -> list[dict]:
    """Define the candidate models and hyperparameters to evaluate."""
    return [
        {
            "classifier": [LogisticRegression(max_iter=1000)],
            "classifier__C": [0.1, 1.0, 10.0],
            "classifier__class_weight": [None, "balanced"],
        },
        {
            "classifier": [
                DecisionTreeClassifier(random_state=RANDOM_STATE)
            ],
            "classifier__max_depth": [3, 5, 10, None],
            "classifier__min_samples_leaf": [2, 10],
            "classifier__class_weight": [None, "balanced"],
        },
        {
            "classifier": [
                RandomForestClassifier(
                    random_state=RANDOM_STATE,
                    n_jobs=1,
                )
            ],
            "classifier__n_estimators": [100, 200],
            "classifier__max_depth": [None, 10],
            "classifier__min_samples_leaf": [1, 2, 5],
            "classifier__class_weight": [None, "balanced"],
        },
    ]


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    if TARGET not in df.columns:
        raise ValueError(f"Dataset must contain '{TARGET}'")

    if df[TARGET].isna().any():
        raise ValueError("Target column contains missing values")

    if not set(df[TARGET].unique()).issubset({0, 1}):
        raise ValueError("Target must contain only 0 and 1")

    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    # Keep the test set separate from hyperparameter search.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    cv = StratifiedKFold(
        n_splits=CV_FOLDS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    search = GridSearchCV(
        estimator=build_pipeline(),
        param_grid=build_parameter_grid(),
        scoring={
            "f1": "f1",
            "precision": "precision",
            "recall": "recall",
            "roc_auc": "roc_auc",
            "accuracy": "accuracy",
        },
        refit="f1",
        cv=cv,
        n_jobs=-1,
        verbose=1,
        return_train_score=True,
        error_score="raise",
    )

    print(f"Training rows: {len(X_train)}")
    print(f"Held-out test rows: {len(X_test)}")
    print(f"Cross-validation folds: {CV_FOLDS}")
    print("\nStarting hyperparameter search...\n")

    # GridSearchCV fits only on the training partition.
    search.fit(X_train, y_train)

    results = pd.DataFrame(search.cv_results_)
    results = results.sort_values("rank_test_f1")

    leaderboard = results[
        [
            "rank_test_f1",
            "mean_test_f1",
            "std_test_f1",
            "mean_test_precision",
            "mean_test_recall",
            "mean_test_roc_auc",
            "mean_test_accuracy",
            "mean_train_f1",
            "params",
        ]
    ].copy()

    leaderboard.to_csv(RESULTS_PATH, index=False)

    print("\nTop 10 configurations by mean CV F1:")
    print(leaderboard.head(10).to_string(index=False))

    print("\nBest cross-validation F1:")
    print(f"{search.best_score_:.4f}")

    print("\nBest hyperparameters:")
    print(search.best_params_)

    print("\nBest pipeline:")
    print(search.best_estimator_)

    # One held-out evaluation of the selected configuration.
    # Do not change the search based on this test result.
    best_model = search.best_estimator_
    probabilities = best_model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

    print("\nHeld-out test metrics (threshold = 0.50)")
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

    print(f"\nSaved tuning leaderboard to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
