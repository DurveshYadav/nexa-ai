
# Customer Churn Dataset — Data Dictionary

## Dataset Overview

- **File:** `customer_churn.csv`
- **Records:** 5,000 synthetic customer records
- **Features:** 7
- **Target:** `churn`
- **Purpose:** Educational customer churn prediction project
- **Source:** Generated locally using `generate_dataset.py`
- **Random seed:** 42

## Columns

| Column | Type | Description |
|---|---|---|
| `customer_age` | Integer | Customer age in years |
| `tenure` | Integer | Customer tenure in months |
| `monthly_spend` | Float | Monthly customer spend in illustrative units |
| `contract_type` | Categorical | `monthly`, `yearly`, or `two_year` |
| `support_tickets` | Integer | Number of support tickets |
| `usage_frequency` | Categorical | `low`, `medium`, or `high` |
| `payment_method` | Categorical | `card`, `bank_transfer`, `upi`, or `cash` |
| `churn` | Integer | Target: `0` = stayed, `1` = churned |

## Data Limitations

- All records are synthetic, not real customer data.
- Churn labels are generated using illustrative rules.
- Relationships in this dataset do not establish real-world customer behavior.
- No model training has been performed in this phase.
- Features represent information assumed to be available before the churn outcome.

