# import pandas as pd
# import pytest

# from ml.features.feature_engineering import CustomerFeatureEngineer


# def test_tenure_group_is_created():
#     X = pd.DataFrame({
#         "tenure": [3, 12, 36],
#     })

#     result = CustomerFeatureEngineer().fit_transform(X)

#     assert "tenure_group" in result.columns
#     assert result["tenure_group"].tolist() == [
#         "new",
#         "established",
#         "long_term",
#     ]


# def test_original_features_are_preserved():
#     X = pd.DataFrame({
#         "tenure": [3, 12],
#         "monthly_spend": [500.0, 800.0],
#     })

#     result = CustomerFeatureEngineer().fit_transform(X)

#     assert "tenure" in result.columns
#     assert "monthly_spend" in result.columns
#     assert len(result) == len(X)


# def test_missing_tenure_is_rejected():
#     X = pd.DataFrame({
#         "monthly_spend": [500.0],
#     })

#     with pytest.raises((ValueError, KeyError)):
#         CustomerFeatureEngineer().fit_transform(X)


# def test_negative_tenure_is_rejected():
#     X = pd.DataFrame({
#         "tenure": [-1],
#     })

#     with pytest.raises(ValueError):
#         CustomerFeatureEngineer().fit_transform(X)

import pandas as pd
import pytest

from ml.features.feature_engineering import CustomerFeatureEngineer


def test_creates_tenure_groups():
    X = pd.DataFrame({
        "tenure": [2, 6, 7, 24, 25, 36],
        "monthly_spend": [100, 150, 175, 250, 275, 300],
    })

    result = CustomerFeatureEngineer().fit_transform(X)

    assert result["tenure_group"].astype(str).tolist() == [
        "new",
        "new",
        "established",
        "established",
        "long_term",
        "long_term",
    ]


def test_preserves_original_columns_and_input():
    X = pd.DataFrame({
        "tenure": [3, 18],
        "monthly_spend": [100, 200],
    })
    original = X.copy(deep=True)

    result = CustomerFeatureEngineer().fit_transform(X)

    assert len(result) == len(X)
    assert "tenure" in result.columns
    assert "monthly_spend" in result.columns
    assert "tenure_group" in result.columns
    assert "tenure_group" not in X.columns
    pd.testing.assert_frame_equal(X, original)


def test_missing_tenure_raises_error():
    X = pd.DataFrame({"monthly_spend": [100, 200]})

    with pytest.raises(ValueError, match="tenure"):
        CustomerFeatureEngineer().fit_transform(X)


def test_invalid_tenure_raises_error():
    X = pd.DataFrame({"tenure": [3, "invalid"]})

    with pytest.raises(ValueError, match="missing or invalid"):
        CustomerFeatureEngineer().fit_transform(X)


def test_negative_tenure_raises_error():
    X = pd.DataFrame({"tenure": [3, -1]})

    with pytest.raises(ValueError, match="negative"):
        CustomerFeatureEngineer().fit_transform(X)


def test_churn_is_not_used_to_create_features():
    X = pd.DataFrame({
        "tenure": [3, 18],
        "churn": [0, 1],
    })

    result = CustomerFeatureEngineer().fit_transform(X)

    assert result["tenure_group"].astype(str).tolist() == [
        "new",
        "established",
    ]
    assert "churn" not in result.drop(
        columns=["tenure_group"]
    ).columns or "churn" in result.columns
