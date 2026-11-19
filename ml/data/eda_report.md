# NexaAI V2 — Exploratory Data Analysis Report

## 1. Dataset Overview

- **Dataset:** `customer_churn.csv`
- **Rows:** 5,000
- **Columns:** 8
- **Purpose:** Explore customer data and identify patterns associated with churn.
- **Data source:** Synthetically generated data for learning and experimentation.

## 2. Data Quality

- Missing values: 0
- Duplicate rows: 0
- Numerical and categorical columns were inspected.
- No immediate data-quality issues were identified in the validation and EDA checks.

## 3. Target Distribution

| Churn value | Meaning | Count | Percentage |
|---|---|---:|---:|
| 0 | Stayed | 3,400 | 68% |
| 1 | Churned | 1,600 | 32% |
| **Total** | | **5,000** | **100%** |

The target classes are imbalanced, but both classes have substantial representation. We should consider this when evaluating the model.

## 4. Numerical Feature Findings

- Average customer age is approximately 46.42 years.
- Average tenure is approximately 36.08 months.
- Average monthly spend is approximately 2,743.84.
- Average support tickets is approximately 2.02.

Compared with customers who stayed, churned customers have lower average tenure and slightly higher average support tickets.

## 5. Categorical Feature Findings

### Contract Type

- Monthly: 40.60% churn
- Two-year: 24.59% churn
- Yearly: 22.90% churn

Monthly contracts have the highest observed churn rate.

### Usage Frequency

- Low: 44.72% churn
- Medium: 27.55% churn
- High: 27.65% churn

Low usage has the highest observed churn rate.

### Payment Method

- Bank transfer: 30.94%
- Card: 31.99%
- Cash: 32.98%
- UPI: 32.09%

Churn rates are relatively similar across payment methods.

## 6. Outlier Analysis

The IQR method identified 26 potential outliers in `support_tickets`. No potential outliers were detected in the other numerical features.

These observations will not be removed automatically because high support-ticket counts may contain useful information.

## 7. Target Leakage Review

No input column is an obvious direct copy of the target. The seven customer attributes will be considered candidate predictors, and `churn` will be the prediction target.

Before production use, feature availability at prediction time must be verified. Since this dataset is synthetic, the observed patterns may reflect the rules used to generate the target.

## 8. Conclusion

Contract type and usage frequency show the clearest differences in observed churn rates. Tenure and support tickets also show differences in their averages.

The dataset is suitable for continuing the educational ML workflow. These observations are exploratory and do not establish causal relationships or real-world predictive performance.

**Next step:** Prepare the preprocessing pipeline and establish a train/test split before training a classification model.
