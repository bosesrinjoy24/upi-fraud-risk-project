# UPI Fraud Risk Profiling

**Business question:** Which transaction patterns in a UPI payment flow are most predictive of fraud, and what is the precision-recall trade-off at different risk thresholds?

**Decision maker:** A fraud risk team lead at a fintech or payment service provider.

## ABOUT

An end-to-end fraud risk analytics project on 100,000 synthetic UPI transactions. This project demonstrates production-grade data science practices including data validation, leakage-safe preprocessing, grouped cross-validation, automated testing, and business-cost simulation. All analytical findings are reported honestly, including mathematically verified null results.

## Data

- **Source:** [Kaggle - UPI Fraud Detection](https://www.kaggle.com/datasets/sameerbhatt12/upi-fraud-detection)
- **Shape:** 100,000 rows x 20 columns
- **Target:** `fraud` (0 = genuine, 1 = fraudulent)
- **Fraud rate:** 23.986% (23,986 / 100,000)
- **Synthetic dataset caveat:** real UPI fraud is <0.1% of traffic. The 24% rate is roughly 240x real-world. Used for methodological practice.

## Technical Architecture (Phase 1 Complete)

The project is fully modularized for reproducibility and engineered to prevent data leakage.

```text
upi-fraud-risk-project/
├── README.md
├── requirements.txt
├── src/
│   ├── data_loader.py
│   ├── validation.py
│   ├── features.py
│   ├── modeling.py
│   └── cost_simulator.py
├── scripts/
│   └── run_pipeline.py
├── tests/
│   └── test_data.py
├── data/
│   └── UPI_FRAUD_100K.csv (not committed)
├── sql/
│   ├── 01_velocity.sql
│   └── 02_device_concentration.sql
├── outputs/
│   ├── cost_simulation.csv
│   └── permutation_importance.csv
└── memo/
    └── UPI_Fraud_Project_Summary.pdf

## Methodology & Key Corrections

During the audit and development of this pipeline, several critical data science best practices were implemented:
1. **Data Leakage Correction:** Removed `Transaction_Status` (Completed/Failed/Pending). A real-time model cannot know the final status at the time of scoring.
2. **Leakage-Safe Preprocessing:** Uses `ColumnTransformer` and `Pipeline` to ensure One-Hot Encoding and Scaling are fitted *only* on the training set.
3. **Grouped Validation:** Uses `GroupShuffleSplit` by `Customer_ID` to prevent the model from memorizing customer-specific patterns.

## Findings & Null Results

**SQL Layer:**
- **Velocity:** Fraud rate is flat across all time-gap buckets (19.23% to 24.35% vs baseline 23.99%).
- **Device Concentration:** 647 customers = 647 devices. 1:1 mapping. No mule-ring signal.

**Machine Learning:**
Both Logistic Regression and Random Forest confirmed a mathematically complete null result.
- **ROC-AUC:** ~0.50 for both models (equivalent to a coin flip).
- **Permutation Importance:** The highest feature (`Device_OS`) had an importance of just 0.0047. 
- **Cost Simulation:** At threshold 0.3, the model flags every transaction (19,924 false positives), costing the business ₹303,100 in investigations. At 0.7, it misses all fraud, costing ₹2.38 million.

**Conclusion:** The synthetic dataset has no learnable behavioral signal. The pipeline is proven correct; the data is the limitation.

## Dashboard

**Screenshot:** [`outputs/06_dashboard_screenshot.png`](outputs/06_dashboard_screenshot.png)

The dashboard visualizes the null results to verify the findings quickly.

## How to Run

1. `pip install -r requirements.txt`
2. Place `UPI_FRAUD_100K.csv` in the `data/` folder.
3. Run the pipeline: `python scripts/run_pipeline.py`
4. Run tests: `python -m pytest tests/ -v`

## Status

- [x] Data inspection
- [x] SQL layer - velocity null, device concentration null
- [x] Python modeling - leakage removed, ROC-AUC = 0.50, null confirmed
- [x] Power BI dashboard built
- [x] Phase 1 Engineering: Validation, Preprocessing Pipelines, Grouped Splits, Automated Tests
- [x] Business Cost Simulation
- [x] One-page insight memo (PDF)

## Business Memo

[Download the final one-page Business Memo (PDF)](memo/UPI_Fraud_Project_Summary.pdf)
