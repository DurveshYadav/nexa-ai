import numpy as np
import pandas as pd

from ml.preprocessing.prepare_data import build_preprocessor


def test_preprocessor_handles_missing_values():
    X = pd.DataFrame({
        "customer_age": [25.0, None, 45.0],
        "tenure": [3.0, 12.0, 36.0],
        "monthly_spend": [500.0, 700.0, 900.0],
        "support_tickets": [0.0, 2.0, 1.0],
        "contract_type": ["monthly", None, "annual"],
        "usage_frequency": ["low", "medium", "high"],
        "payment_method": ["card", "cash", "card"],
        "tenure_group": ["new", "established", "long_term"],
    })

    preprocessor = build_preprocessor()
    transformed = preprocessor.fit_transform(X)

    # All input rows should be preserved.
    assert transformed.shape[0] == len(X)

    # Preprocessing should produce numeric features.
    assert transformed.shape[1] > 0

    # Imputation should prevent missing values from reaching the output.
    values = (
        transformed.toarray()
        if hasattr(transformed, "toarray")
        else np.asarray(transformed)
    )
    assert np.isfinite(values).all()


def test_preprocessor_handles_unknown_categories():
    train = pd.DataFrame({
        "customer_age": [25.0, 40.0, 35.0],
        "tenure": [3.0, 36.0, 12.0],
        "monthly_spend": [500.0, 900.0, 700.0],
        "support_tickets": [0.0, 1.0, 2.0],
        "contract_type": ["monthly", "annual", "monthly"],
        "usage_frequency": ["low", "high", "medium"],
        "payment_method": ["card", "cash", "card"],
        "tenure_group": ["new", "long_term", "established"],
    })

    inference = train.iloc[[0]].copy()
    inference.loc[:, "contract_type"] = "unseen_contract"

    preprocessor = build_preprocessor()
    preprocessor.fit(train)
    transformed = preprocessor.transform(inference)

    assert transformed.shape[0] == 1
    assert transformed.shape[1] > 0

    values = (
        transformed.toarray()
        if hasattr(transformed, "toarray")
        else np.asarray(transformed)
    )
    assert np.isfinite(values).all()
