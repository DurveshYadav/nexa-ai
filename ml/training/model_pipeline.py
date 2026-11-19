
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from ml.features.feature_engineering import CustomerFeatureEngineer
# from ml.features.preprocessing import build_preprocessor
from ml.preprocessing.prepare_data import build_preprocessor


RANDOM_STATE = 42


def build_classifier(
    model_name: str,
    params: dict | None = None,
) -> BaseEstimator:
    """Create a supported classifier with explicit hyperparameters."""
    params = params or {}

    classifiers = {
        "Logistic Regression": {
            "estimator": LogisticRegression(max_iter=1000),
            "allowed_params": {"C", "class_weight"},
        },
        "Decision Tree": {
            "estimator": DecisionTreeClassifier(
                random_state=RANDOM_STATE
            ),
            "allowed_params": {
                "max_depth",
                "min_samples_leaf",
                "class_weight",
            },
        },
        "Random Forest": {
            "estimator": RandomForestClassifier(
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "allowed_params": {
                "n_estimators",
                "max_depth",
                "min_samples_leaf",
                "class_weight",
            },
        },
    }

    if model_name not in classifiers:
        raise ValueError(
            f"Unsupported model: {model_name}. "
            f"Choose one of {list(classifiers)}"
        )

    allowed = classifiers[model_name]["allowed_params"]
    invalid = set(params) - allowed

    if invalid:
        raise ValueError(
            f"Unsupported parameters for {model_name}: {sorted(invalid)}"
        )

    estimator = classifiers[model_name]["estimator"]
    estimator.set_params(**params)

    return estimator


def build_pipeline(
    model_name: str,
    params: dict | None = None,
) -> Pipeline:
    """Build a complete, reusable customer churn pipeline."""
    classifier = build_classifier(model_name, params)

    return Pipeline(
        steps=[
            ("feature_engineering", CustomerFeatureEngineer()),
            ("preprocessing", build_preprocessor()),
            ("classifier", classifier),
        ]
    )
