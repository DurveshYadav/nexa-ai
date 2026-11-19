
from pathlib import Path

import pandas as pd


# Project root: two levels above ml/notebooks/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT / "ml" / "data" / "customer_churn.csv"
)


def load_dataset() -> pd.DataFrame:
    """Load the customer churn dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    return pd.read_csv(DATASET_PATH)


def main() -> None:
    df = load_dataset()

    print("=== NexaAI V2: Exploratory Data Analysis ===")

    # 1. Dataset dimensions
    print("\n1. Dataset shape:")
    print(df.shape)

    # 2. First five records
    print("\n2. First five records:")
    print(df.head())

    # 3. Column names
    print("\n3. Column names:")
    print(df.columns.tolist())

    # 4. Data types
    print("\n4. Data types:")
    print(df.dtypes)

    # 5. Dataset information
    print("\n5. Dataset information:")
    df.info()

    # 6. Numerical summary statistics
    print("\n6. Numerical summary:")
    print(df.describe())

    # 7. Categorical summary
    print("\n7. Categorical summary:")
    # print(df.describe(include="object"))
    print(df.describe(include=["str", "object"]))
    
    
    # 8. Missing values
    print("\n8. Missing values:")
    print(df.isnull().sum())

    print("\nMissing value percentages:")
    missing_percent = df.isnull().mean() * 100
    print(missing_percent.round(2))

    # 9. Duplicate records
    print("\n9. Duplicate records:")
    duplicate_count = df.duplicated().sum()
    print(f"Total duplicate rows: {duplicate_count}")

    # 10. Churn target distribution
    print("\n10. Churn distribution:")
    churn_counts = df["churn"].value_counts().sort_index()
    print(churn_counts)

    print("\nChurn percentages:")
    churn_percentages = (
        df["churn"].value_counts(normalize=True).sort_index() * 100
    )
    print(churn_percentages.round(2))

    # 11. Categorical feature distributions
    print("\n11. Categorical feature distributions:")
    categorical_columns = [
        "contract_type",
        "usage_frequency",
        "payment_method",
    ]

    for column in categorical_columns:
        print(f"\n{column}:")
        print(df[column].value_counts())


    # 12. Numerical feature analysis
    print("\n12. Numerical feature analysis:")

    numerical_columns = [
        "customer_age",
        "tenure",
        "monthly_spend",
        "support_tickets",
    ]

    print(df[numerical_columns].describe().round(2))

    # 13. Outlier detection using IQR
    print("\n13. Potential outliers using IQR:")

    for column in numerical_columns:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = df[
            (df[column] < lower_bound)
            | (df[column] > upper_bound)
        ]

        print(f"\nFeature: {column}")
        print(f"Q1: {q1:.2f}")
        print(f"Q3: {q3:.2f}")
        print(f"IQR: {iqr:.2f}")
        print(f"Lower bound: {lower_bound:.2f}")
        print(f"Upper bound: {upper_bound:.2f}")
        print(f"Potential outlier count: {len(outliers)}")


    # 14. Numerical features versus churn
    print("\n14. Numerical features versus churn:")

    numerical_columns = [
        "customer_age",
        "tenure",
        "monthly_spend",
        "support_tickets",
    ]

    churn_comparison = df.groupby("churn")[numerical_columns].mean()
    print(churn_comparison.round(2))

    # 15. Categorical features versus churn
    print("\n15. Categorical features versus churn:")

    categorical_columns = [
        "contract_type",
        "usage_frequency",
        "payment_method",
    ]

    for column in categorical_columns:
        print(f"\nChurn rate by {column} (%):")

        churn_rate = (
            df.groupby(column, observed=True)["churn"]
            .mean()
            .mul(100)
            .round(2)
        )

        print(churn_rate)

    # 16. Contract type versus churn
    print("\n16. Churn counts by contract type:")
    print(pd.crosstab(df["contract_type"], df["churn"]))



if __name__ == "__main__":
    main()
