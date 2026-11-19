
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CustomerFeatureEngineer(BaseEstimator, TransformerMixin):
    """Create derived features for customer churn prediction."""

    def fit(self, X, y=None):
        # The rules are fixed, so no data needs to be learned.
        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("X must be a pandas DataFrame")

        if "tenure" not in X.columns:
            raise ValueError("Required feature 'tenure' is missing")

        result = X.copy()

        tenure = pd.to_numeric(result["tenure"], errors="coerce")

        if tenure.isna().any():
            raise ValueError(
                "'tenure' contains missing or invalid values"
            )

        if (tenure < 0).any():
            raise ValueError("'tenure' cannot be negative")

        result["tenure_group"] = pd.cut(
            tenure,
            bins=[-float("inf"), 6, 24, float("inf")],
            labels=["new", "established", "long_term"],
            right=True,
        )

        return result
