
from pathlib import Path

import numpy as np
import pandas as pd


def generate_dataset(
    n_rows: int = 5000,
    random_state: int = 42,
) -> pd.DataFrame:
    """Generate synthetic customer churn data for learning."""

    rng = np.random.default_rng(random_state)

    # 1. Generate customer features
    customer_age = rng.integers(18, 76, size=n_rows)
    tenure = rng.integers(1, 73, size=n_rows)
    monthly_spend = np.round(
        rng.uniform(500, 5000, size=n_rows), 2
    )

    contract_type = rng.choice(
        ["monthly", "yearly", "two_year"],
        size=n_rows,
        p=[0.5, 0.3, 0.2],
    )

    support_tickets = rng.poisson(2, size=n_rows)

    usage_frequency = rng.choice(
        ["low", "medium", "high"],
        size=n_rows,
        p=[0.25, 0.45, 0.30],
    )

    payment_method = rng.choice(
        ["card", "bank_transfer", "upi", "cash"],
        size=n_rows,
    )

    # 2. Create an educational churn probability
    logit = (
        -1.2
        + (contract_type == "monthly") * 0.9
        + (usage_frequency == "low") * 0.8
        + (support_tickets >= 4) * 0.6
        - (tenure / 72) * 0.8
    )

    churn_probability = 1 / (1 + np.exp(-logit))

    # 3. Generate the target: 0 = stayed, 1 = churned
    churn = rng.binomial(1, churn_probability)

    # 4. Combine features and target into a DataFrame
    return pd.DataFrame({
        "customer_age": customer_age,
        "tenure": tenure,
        "monthly_spend": monthly_spend,
        "contract_type": contract_type,
        "support_tickets": support_tickets,
        "usage_frequency": usage_frequency,
        "payment_method": payment_method,
        "churn": churn,
    })


if __name__ == "__main__":
    df = generate_dataset()

    output_path = Path(__file__).with_name("customer_churn.csv")
    df.to_csv(output_path, index=False)

    print(f"Dataset saved to: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print("\nFirst five records:")
    print(df.head())
