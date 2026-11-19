# Power BI Dashboard Guide

## Purpose

The dashboard presents the synthetic dataset profile, descriptive SQL findings, model evaluation, and illustrative business-cost results.

It must communicate the null result honestly and must not imply production readiness.

## Data Sources

Load the following files:

- `outputs/model_metrics.csv`
- `outputs/cost_simulation.csv`
- `outputs/oof_predictions.csv`
- `data/UPI_FRAUD_100K.csv`

The raw transaction CSV is locally available and may be excluded from Git according to the repository's data-handling policy.

## Page 1: Executive Fraud Overview

Suggested visuals:

- Card: 100,000 transactions.
- Card: 23.986% observed fraud share.
- Card: 23,986 fraud-labelled transactions.
- Text: dataset is synthetic; this class share is not real-world UPI fraud prevalence.
- Text: Logistic Regression and Random Forest achieved near-chance ROC-AUC.

## Page 2: Transaction and SQL Investigations

Suggested visuals:

- Bar chart: fraud rate by hour, calculated from the raw transaction dataset using the transaction timestamp and `fraud` label.
- Table: transaction velocity buckets from `sql/01_velocity.sql`.
- Table: device and IP reuse findings from `sql/02_device_concentration.sql`.

The velocity analysis included 99,353 transactions because first transactions per customer have no preceding transaction.

The top-ten device and customer queries each returned one unique customer per device and one unique device per customer in their respective result sets. Two IP addresses were each observed across two customers. These are descriptive findings, not proof of fraud.

The SQL analysis confirms each device maps to exactly one customer and each customer maps to exactly one device in the inspected data, with zero shared devices.

## Page 3: Model and Operational Performance

Suggested visuals:

- Table or bar chart using `model_metrics.csv`.
- Line chart: `Threshold` on the X-axis and `Total_Cost` on the Y-axis from `cost_simulation.csv`.
- Tooltips: use the actual available columns, including `Flagged`, `TP`, `FP`, and `FN`, after confirming their exact names in the CSV.
- Text explaining the illustrative cost assumptions: ₹20 per investigation and ₹500 per missed fraud.

Verified reference results:

| Threshold | Total cost |
|---:|---:|
| 0.3 | ₹2,000,000 |
| 0.5 | ₹8,206,660 |
| 0.7 | ₹11,993,000 |

The Random Forest out-of-fold probabilities range from 0.416947 to 0.572974, with a mean of 0.495102. Therefore, threshold 0.3 flags all transactions and threshold 0.7 flags none. The model does not provide a useful operational fraud filter in this evaluation.

## Dashboard Integrity

- Use `Total_Cost`, not `Total_Cost_INR`.
- `oof_predictions.csv` contains `y_true` and `y_proba_rf`; it does not contain the transaction hour.
- Use the raw transaction dataset for fraud rate by hour.
- Clearly label all data as synthetic.
- Do not present scenario costs as actual bank losses.
- Save the Power BI file as `dashboard/UPI_Fraud_Dashboard_Final.pbix`.
