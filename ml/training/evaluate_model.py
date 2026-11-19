
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
    StratifiedKFold,
    cross_val_predict,
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

# Replace this with the winner from your Phase 7 CV table.
SELECTED_MODEL_NAME = "Random Forest"


def build_model(name):
    classifiers = {
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

    if name not in classifiers:
        raise ValueError(
            f"Unknown model: {name}. "
            f"Choose one of {list(classifiers)}"
        )

    return Pipeline(steps=[
        ("feature_engineering", CustomerFeatureEngineer()),
        ("preprocessing", build_preprocessor()),
        ("classifier", classifiers[name]),
    ])


def print_metrics(y_true, probabilities, threshold, title):
    predictions = (probabilities >= threshold).astype(int)

    print(f"\n--- {title} ---")
    print(f"Threshold: {threshold:.3f}")
    print(f"Accuracy:  {accuracy_score(y_true, predictions):.4f}")
    print(
        f"Precision: {precision_score(y_true, predictions, zero_division=0):.4f}"
    )
    print(
        f"Recall:    {recall_score(y_true, predictions, zero_division=0):.4f}"
    )
    print(f"F1:        {f1_score(y_true, predictions, zero_division=0):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_true, probabilities):.4f}")
    print("\nConfusion matrix (actual rows, predicted columns):")
    print(confusion_matrix(y_true, predictions, labels=[0, 1]))
    print("\nClassification report:")
    print(
        classification_report(
            y_true,
            predictions,
            labels=[0, 1],
            target_names=["No churn (0)", "Churn (1)"],
            zero_division=0,
        )
    )
    return predictions


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

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Generate out-of-fold probabilities using training data only.
    # Each training row is predicted by a model that did not fit on it.
    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    model = build_model(SELECTED_MODEL_NAME)

    train_oof_probabilities = cross_val_predict(
        model,
        X_train,
        y_train,
        cv=cv,
        method="predict_proba",
        n_jobs=1,
    )[:, 1]

    # Choose a threshold based on training out-of-fold F1.
    # This is an educational selection rule, not a universal optimum.
    thresholds = [i / 100 for i in range(10, 91, 5)]
    threshold_scores = [
        (
            threshold,
            f1_score(
                y_train,
                (train_oof_probabilities >= threshold).astype(int),
                zero_division=0,
            ),
        )
        for threshold in thresholds
    ]
    best_threshold, best_oof_f1 = max(
        threshold_scores, key=lambda item: item[1]
    )

    print("Selected model:", SELECTED_MODEL_NAME)
    print("Training rows:", len(X_train))
    print("Test rows:", len(X_test))
    print(f"Best training OOF F1: {best_oof_f1:.4f}")
    print(f"Selected threshold: {best_threshold:.2f}")

    # Fit on all training rows only.
    model.fit(X_train, y_train)
    test_probabilities = model.predict_proba(X_test)[:, 1]

    default_predictions = print_metrics(
        y_test,
        test_probabilities,
        0.50,
        "Held-out test results: default threshold",
    )

    selected_predictions = print_metrics(
        y_test,
        test_probabilities,
        best_threshold,
        "Held-out test results: training-selected threshold",
    )

    # Investigate mistakes at the selected threshold.
    errors = X_test.copy()
    errors["actual_churn"] = y_test
    errors["predicted_churn"] = selected_predictions
    errors["churn_probability"] = test_probabilities
    errors["error_type"] = "correct"

    errors.loc[
        (errors["actual_churn"] == 0)
        & (errors["predicted_churn"] == 1),
        "error_type",
    ] = "false_positive"

    errors.loc[
        (errors["actual_churn"] == 1)
        & (errors["predicted_churn"] == 0),
        "error_type",
    ] = "false_negative"

    misclassified = errors[
        errors["actual_churn"] != errors["predicted_churn"]
    ]

    print("\nMisclassification counts:")
    print(misclassified["error_type"].value_counts())

    print("\nFirst 10 misclassified test rows:")
    print(misclassified.head(10).to_string())

    # Save errors for local investigation; do not commit them blindly.
    output_path = PROJECT_ROOT / "ml" / "training" / "evaluation_errors.csv"
    misclassified.to_csv(output_path, index=True)
    print(f"\nMisclassified rows saved to: {output_path}")


if __name__ == "__main__":
    main()
