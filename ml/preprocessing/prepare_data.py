
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from ml.features.feature_engineering import CustomerFeatureEngineer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "ml" / "data" / "customer_churn.csv"

NUMERICAL_FEATURES = [
    "customer_age",
    "tenure",
    "monthly_spend",
    "support_tickets",
]

# CATEGORICAL_FEATURES = [
#     "contract_type",
#     "usage_frequency",
#     "payment_method",
# ]

CATEGORICAL_FEATURES = [
    "contract_type",
    "usage_frequency",
    "payment_method",
    "tenure_group",
]

RAW_CATEGORICAL_FEATURES = [
    "contract_type",
    "usage_frequency",
    "payment_method",
]

TARGET = "churn"


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    return pd.read_csv(DATA_PATH)


def build_preprocessor() -> ColumnTransformer:
    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numerical", numerical_pipeline, NUMERICAL_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def prepare_data() -> None:
    df = load_dataset()

    # Build X without the target column.
    raw_features = NUMERICAL_FEATURES + RAW_CATEGORICAL_FEATURES
    X = df[raw_features].copy()
    y = df[TARGET].copy()

    # Split first to keep the workflow safe for future learned transforms.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # Step 1: Create derived features.
    feature_engineer = CustomerFeatureEngineer()
    X_train_engineered = feature_engineer.fit_transform(X_train)
    X_test_engineered = feature_engineer.transform(X_test)

    # Step 2: Fit preprocessing on training data only.
    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train_engineered)
    X_test_processed = preprocessor.transform(X_test_engineered)

    print("=== NexaAI V2: Feature Engineering + Preprocessing ===")
    print(f"Original dataset: {df.shape}")
    print(f"Raw feature columns: {X.shape[1]}")
    print(f"Engineered training columns: {X_train_engineered.columns.tolist()}")
    print(f"Training features: {X_train.shape}")
    print(f"Test features: {X_test.shape}")
    print(f"Processed training features: {X_train_processed.shape}")
    print(f"Processed test features: {X_test_processed.shape}")
    print(f"Target included in input features: {TARGET in X.columns}")

    print("\nTraining target distribution:")
    print(y_train.value_counts().sort_index())

    print("\nTest target distribution:")
    print(y_test.value_counts().sort_index())

    print("\nFeature engineering and preprocessing completed successfully.")

# def prepare_data() -> None:
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

#     preprocessor = build_preprocessor()

#     # Fit on training data only; transform both datasets.
#     X_train_processed = preprocessor.fit_transform(X_train)
#     X_test_processed = preprocessor.transform(X_test)

#     print("=== NexaAI V2: Data Preprocessing ===")
#     print(f"Original dataset: {df.shape}")
#     print(f"Training features: {X_train.shape}")
#     print(f"Test features: {X_test.shape}")
#     print(f"Training target: {y_train.shape}")
#     print(f"Test target: {y_test.shape}")
#     print(f"Processed training features: {X_train_processed.shape}")
#     print(f"Processed test features: {X_test_processed.shape}")

#     print("\nTraining target distribution:")
#     print(y_train.value_counts().sort_index())

#     print("\nTest target distribution:")
#     print(y_test.value_counts().sort_index())

#     print("\nPreprocessing completed successfully.")


if __name__ == "__main__":
    prepare_data()
