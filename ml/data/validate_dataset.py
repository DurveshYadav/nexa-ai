
from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).with_name("customer_churn.csv")

EXPECTED_COLUMNS = {
    "customer_age",
    "tenure",
    "monthly_spend",
    "contract_type",
    "support_tickets",
    "usage_frequency",
    "payment_method",
    "churn",
}

NUMERICAL_FEATURES = [
    "customer_age",
    "tenure",
    "monthly_spend",
    "support_tickets",
]

CATEGORICAL_FEATURES = [
    "contract_type",
    "usage_frequency",
    "payment_method",
]

TARGET = "churn"

VALID_CATEGORIES = {
    "contract_type": {"monthly", "yearly", "two_year"},
    "usage_frequency": {"low", "medium", "high"},
    "payment_method": {"card", "bank_transfer", "upi", "cash"},
}

VALID_TARGET_VALUES = {0, 1}


def validate_dataset() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print("=== NexaAI V2: Dataset Validation ===")

    # 1. Basic structure
    print("\n1. Dataset shape:", df.shape)
    print("Columns:", df.columns.tolist())

    assert len(df) == 5000, f"Expected 5000 rows, found {len(df)}"
    assert df.columns.is_unique, "Duplicate column names found"

    actual_columns = set(df.columns)
    missing_columns = EXPECTED_COLUMNS - actual_columns
    unexpected_columns = actual_columns - EXPECTED_COLUMNS

    print("\n2. Schema validation")
    print("Missing columns:", missing_columns)
    print("Unexpected columns:", unexpected_columns)

    assert not missing_columns, f"Missing columns: {missing_columns}"
    assert not unexpected_columns, f"Unexpected columns: {unexpected_columns}"

    # 2. Data types
    print("\n3. Data types")
    print(df.dtypes)

    for column in NUMERICAL_FEATURES:
        assert pd.api.types.is_numeric_dtype(df[column]), (
            f"{column} must be numeric"
        )

    for column in CATEGORICAL_FEATURES:
        assert pd.api.types.is_string_dtype(df[column]), (
            f"{column} must contain strings"
        )

    assert pd.api.types.is_integer_dtype(df[TARGET]), (
        f"{TARGET} must contain integer labels"
    )

    # 3. Missing values
    missing_counts = df.isnull().sum()

    print("\n4. Missing values")
    print(missing_counts)

    assert not df.isnull().any().any(), "Missing values found"

    # 4. Duplicate rows
    duplicate_count = int(df.duplicated().sum())
    print("\n5. Duplicate rows:", duplicate_count)

    assert duplicate_count == 0, "Duplicate rows found"

    # 5. Numerical range validation
    range_rules = {
        "customer_age": (18, 75),
        "tenure": (1, 72),
        "monthly_spend": (500, 5000),
    }

    print("\n6. Numerical range validation")

    for column, (minimum, maximum) in range_rules.items():
        valid = df[column].between(minimum, maximum).all()
        print(f"{column}: {minimum} to {maximum} -> {valid}")
        assert valid, f"Invalid values found in {column}"

    assert df["support_tickets"].ge(0).all(), (
        "support_tickets cannot be negative"
    )

    assert pd.api.types.is_integer_dtype(df["support_tickets"]), (
        "support_tickets must contain whole numbers"
    )

    # 6. Target validation
    actual_target_values = set(df[TARGET].unique())
    unexpected_targets = actual_target_values - VALID_TARGET_VALUES

    print("\n7. Target validation")
    print("Target values:", actual_target_values)
    print("Unexpected target values:", unexpected_targets)

    assert not unexpected_targets, (
        f"Unexpected target values: {unexpected_targets}"
    )
    assert actual_target_values == VALID_TARGET_VALUES, (
        "Both churn classes 0 and 1 must exist"
    )

    print("\nChurn distribution")
    print(df[TARGET].value_counts().sort_index())

    print("\nChurn proportions")
    print(df[TARGET].value_counts(normalize=True).sort_index().round(3))

    # 7. Categorical validation
    print("\n8. Categorical validation")

    for column, valid_values in VALID_CATEGORIES.items():
        actual_values = set(df[column].unique())
        unexpected_values = actual_values - valid_values

        print(f"{column}: {actual_values}")
        print(f"Unexpected values: {unexpected_values}")

        assert not unexpected_values, (
            f"Invalid categories in {column}: {unexpected_values}"
        )

    print("\n9. Feature configuration")
    print("Numerical features:", NUMERICAL_FEATURES)
    print("Categorical features:", CATEGORICAL_FEATURES)
    print("Target:", TARGET)

    print("\nAll dataset validation checks passed!")


if __name__ == "__main__":
    validate_dataset()
