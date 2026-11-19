# Data

- **Source:** [UPI Fraud Detection — Kaggle](https://www.kaggle.com/datasets/sameerbhatt12/upi-fraud-detection)
- **File:** `UPI_FRAUD_100K.csv` (100,000 rows, 20 columns, 25.37 MB)
- **Target column:** `fraud` (0 = genuine, 1 = fraudulent)
- **Fraud rate:** 23.986% (23,986 fraudulent / 100,000 total)

## Important caveat

This is a **synthetic dataset**. The 24% fraud rate is roughly 240x higher than real-world UPI fraud in India (reported losses of ~Rs 1,000 crore against ~Rs 28 lakh crore monthly transaction value — a rate well under 0.1%). The dataset also contains geographic inconsistencies (city-state mismatches) consistent with generated data.

It is used here for **methodological practice**. The workflow — velocity analysis, device concentration, precision-recall trade-off, threshold selection — transfers directly to production fraud systems. The specific rates and thresholds do not.

## Why the CSV is not committed

At 25.37 MB it exceeds a sensible repository size. Download it from Kaggle and place it in this folder before running the notebooks.
