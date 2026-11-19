import numpy as np
import pandas as pd

from ml.training.model_pipeline import build_pipeline


def sample_training_data():
    X = pd.DataFrame({
        "customer_age": [22, 30, 45, 50, 27, 39, 60, 34],
        "tenure": [2, 8, 30, 40, 4, 18, 50, 12],
        "monthly_spend": [300, 500, 900, 850, 350, 650, 1000, 600],
        "contract_type": [
            "monthly", "annual", "annual", "monthly",
            "monthly", "annual", "annual", "monthly",
        ],
        "support_tickets": [4, 2, 0, 1, 5, 1, 0, 3],
        "usage_frequency": [
            "low", "medium", "high", "high",
            "low", "medium", "high", "medium",
        ],
        "payment_method": [
            "cash", "card", "card", "cash",
            "cash", "card", "card", "cash",
        ],
    })

    y = pd.Series([1, 0, 0, 0, 1, 0, 0, 1], name="churn")
    return X, y


def test_pipeline_fits_and_predicts():
    X, y = sample_training_data()

    pipeline = build_pipeline("Logistic Regression")
    pipeline.fit(X, y)

    predictions = pipeline.predict(X)

    assert len(predictions) == len(X)
    assert set(np.unique(predictions)).issubset({0, 1})


def test_pipeline_probabilities_are_valid():
    X, y = sample_training_data()

    pipeline = build_pipeline("Logistic Regression")
    pipeline.fit(X, y)

    probabilities = pipeline.predict_proba(X)

    assert probabilities.shape == (len(X), 2)
    assert np.isfinite(probabilities).all()
    assert np.all(probabilities >= 0)
    assert np.all(probabilities <= 1)
    assert np.allclose(probabilities.sum(axis=1), 1.0)


def test_target_is_not_a_model_input():
    X, y = sample_training_data()

    assert "churn" not in X.columns

    pipeline = build_pipeline("Logistic Regression")
    pipeline.fit(X, y)

    assert "churn" not in X.columns

# import pandas as pd
# import pytest

# from ml.training.model_pipeline import build_pipeline


# @pytest.fixture
# def sample_data():
#     X = pd.DataFrame(
#         {
#             "customer_age": [25, 40, 32, 55, 29, 48, 36, 61],
#             "tenure": [2, 12, 30, 5, 18, 36, 8, 48],
#             "monthly_spend": [
#                 30.0, 55.0, 70.0, 25.0,
#                 45.0, 80.0, 35.0, 90.0,
#             ],
#             "contract_type": [
#                 "monthly", "yearly", "two_year", "monthly",
#                 "yearly", "two_year", "monthly", "yearly",
#             ],
#             "support_tickets": [3, 1, 0, 4, 2, 0, 2, 1],
#             "usage_frequency": [
#                 "low", "medium", "high", "low",
#                 "medium", "high", "medium", "high",
#             ],
#             "payment_method": [
#                 "card", "upi", "bank_transfer", "cash",
#                 "card", "upi", "cash", "bank_transfer",
#             ],
#         }
#     )

#     y = pd.Series([1, 0, 0, 1, 1, 0, 0, 1], name="churn")
#     return X, y


# def test_pipeline_fits_and_predicts(sample_data):
#     X, y = sample_data
#     model = build_pipeline(
#         "Logistic Regression",
#         {"C": 1.0},
#     )

#     model.fit(X, y)

#     predictions = model.predict(X)
#     probabilities = model.predict_proba(X)

#     assert len(predictions) == len(X)
#     assert set(predictions).issubset({0, 1})
#     assert probabilities.shape == (len(X), 2)
#     assert ((probabilities >= 0) & (probabilities <= 1)).all()


# def test_pipeline_does_not_require_target_as_input(sample_data):
#     X, y = sample_data
#     model = build_pipeline("Decision Tree", {"max_depth": 3})

#     model.fit(X, y)

#     assert "churn" not in X.columns
#     assert "churn" not in model.named_steps["preprocessing"].feature_names_in_


# def test_pipeline_rejects_unknown_model():
#     with pytest.raises(ValueError, match="Unsupported model"):
#         build_pipeline("Unknown Model")


# def test_pipeline_rejects_unknown_hyperparameter():
#     with pytest.raises(ValueError, match="Unsupported parameters"):
#         build_pipeline(
#             "Logistic Regression",
#             {"max_depth": 3},
#         )
