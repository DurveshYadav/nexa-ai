
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from ml.features.feature_engineering import CustomerFeatureEngineer
from ml.preprocessing.prepare_data import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    RAW_CATEGORICAL_FEATURES,
    TARGET,
    build_preprocessor,
    load_dataset,
)


def get_raw_features(df):
    return df[NUMERICAL_FEATURES + RAW_CATEGORICAL_FEATURES].copy()


def test_load_dataset():
    df = load_dataset()

    assert df.shape == (5000, 8)
    assert TARGET in df.columns
    assert df[TARGET].nunique() == 2


def test_target_is_excluded_from_input_features():
    df = load_dataset()

    X = get_raw_features(df)
    y = df[TARGET]

    assert TARGET not in X.columns
    assert len(X) == len(y)
    assert set(y.unique()) == {0, 1}


def test_train_test_split_preserves_target_ratio():
    df = load_dataset()
    X = get_raw_features(df)
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    assert len(X_train) == 4000
    assert len(X_test) == 1000
    assert y_train.mean() == y_test.mean()


def test_feature_engineering_and_preprocessing_output_shape():
    df = load_dataset()
    X = get_raw_features(df)
    y = df[TARGET]

    X_train, X_test, _, _ = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    engineer = CustomerFeatureEngineer()
    X_train_engineered = engineer.fit_transform(X_train)
    X_test_engineered = engineer.transform(X_test)

    assert "tenure_group" in X_train_engineered.columns
    assert TARGET not in X_train_engineered.columns

    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train_engineered)
    X_test_processed = preprocessor.transform(X_test_engineered)

    assert X_train_processed.shape == (4000, 17)
    assert X_test_processed.shape == (1000, 17)


def test_preprocessor_handles_unknown_categories():
    df = load_dataset()
    X = get_raw_features(df)

    engineer = CustomerFeatureEngineer()
    X_engineered = engineer.fit_transform(X)

    preprocessor = build_preprocessor()
    preprocessor.fit(X_engineered)

    new_customer = pd.DataFrame([{
        "customer_age": 35,
        "tenure": 12,
        "monthly_spend": 2500.0,
        "support_tickets": 2,
        "contract_type": "unexpected_contract",
        "usage_frequency": "unexpected_usage",
        "payment_method": "unexpected_payment",
    }])

    new_customer_engineered = engineer.transform(new_customer)
    transformed = preprocessor.transform(new_customer_engineered)

    assert transformed.shape == (1, 17)

    if hasattr(transformed, "toarray"):
        values = transformed.toarray()
    else:
        values = np.asarray(transformed)

    assert np.isfinite(values).all()



# import pytest
# import numpy as np
# import pandas as pd

# from sklearn.model_selection import train_test_split

# from ml.preprocessing.prepare_data import (
#     CATEGORICAL_FEATURES,
#     NUMERICAL_FEATURES,
#     TARGET,
#     build_preprocessor,
#     load_dataset,
# )

# # @pytest.mark.no_database
# def test_load_dataset():
#     df = load_dataset()

#     assert df.shape == (5000, 8)
#     assert TARGET in df.columns
#     assert df[TARGET].nunique() == 2


# def test_train_test_split_preserves_target_ratio():
#     df = load_dataset()

#     X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
#     y = df[TARGET]

#     X_train, X_test, y_train, y_test = train_test_split(
#         X,
#         y,
#         test_size=0.20,
#         random_state=42,
#         stratify=y,
#     )

#     assert len(X_train) == 4000
#     assert len(X_test) == 1000
#     assert len(y_train) == 4000
#     assert len(y_test) == 1000

#     assert y_train.mean() == y_test.mean()


# def test_preprocessor_output_shape():
#     df = load_dataset()

#     X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
#     y = df[TARGET]

#     X_train, X_test, _, _ = train_test_split(
#         X,
#         y,
#         test_size=0.20,
#         random_state=42,
#         stratify=y,
#     )

#     preprocessor = build_preprocessor()

#     X_train_processed = preprocessor.fit_transform(X_train)
#     X_test_processed = preprocessor.transform(X_test)

#     assert X_train_processed.shape == (4000, 14)
#     assert X_test_processed.shape == (1000, 14)


# def test_preprocessor_handles_unknown_categories():
#     df = load_dataset()

#     X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]

#     preprocessor = build_preprocessor()
#     preprocessor.fit(X)

#     new_customer = pd.DataFrame(
#         [
#             {
#                 "customer_age": 35,
#                 "tenure": 12,
#                 "monthly_spend": 2500.0,
#                 "support_tickets": 2,
#                 "contract_type": "unexpected_contract",
#                 "usage_frequency": "unexpected_usage",
#                 "payment_method": "unexpected_payment",
#             }
#         ]
#     )

#     transformed = preprocessor.transform(new_customer)

#     assert transformed.shape == (1, 14)

#     values = (
#         transformed.data
#         if hasattr(transformed, "data") and hasattr(transformed, "tocsr")
#         else transformed
#     )
#     assert np.isfinite(values).all()
    