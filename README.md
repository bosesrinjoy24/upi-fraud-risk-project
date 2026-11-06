# UPI Fraud Risk Analysis

**Business question:** Which transaction patterns in a UPI payment flow are most predictive of fraud, and what is the precision-recall trade-off at different risk thresholds?

**Decision maker:** A fraud risk team lead at a fintech or payment service provider.

## ABOUT

An end-to-end fraud risk analytics project on 100,000 synthetic UPI transactions. The SQL layer tested two of the strongest production fraud signals - transaction velocity and device concentration - and found both structurally absent from this dataset. The remaining behavioral columns are tested in the Python modeling layer. All findings reported honestly, including null results.

## Data

- **Source:** [Kaggle - UPI Fraud Detection](https://www.kaggle.com/datasets/sameerbhatt12/upi-fraud-detection)
- **Shape:** 100,000 rows x 20 columns
- **Target:** `fraud` (0 = genuine, 1 = fraudulent)
- **Fraud rate:** 23.986% (23,986 / 100,000)
- **Synthetic dataset caveat:** real UPI fraud is <0.1% of traffic. The 24% rate is roughly 240x real-world. Used for methodological practice. See [`data/README.md`](data/README.md) for full caveat.

**Structural characteristics:**
- 647 unique customers, ~155 transactions each
- **647 unique devices - 1:1 with customers** (`Device_ID` is a disguised `Customer_ID`)
- 99,998 unique IPs across 100,000 rows (essentially unique per transaction)

## Methods

| Stage | Tools | Status |
|---|---|---|
| Collect | kagglehub, pandas | Done |
| Inspect | pandas (`df.shape`, `.dtypes`, `.isnull().sum()`, `.value_counts()`) | Done |
| SQL layer | SQLite (DB Browser) - window functions, GROUP BY, HAVING | Done |
| Python modeling | pandas, scikit-learn - logistic regression, random forest, precision-recall | Done |
| Dashboard | Power BI Desktop - published report | Done |
| Memo | One-page insight memo (PDF) | Pending |

## Repository Map
upi-fraud-risk-project/
|-- README.md # This file
|-- .gitignore # Excludes *.csv, *.db, *.pbix, checkpoints
|-- data/
| |-- README.md # Source + synthetic caveat
| |-- UPI_FRAUD_100K.csv # 25.37 MB (not committed)
| +-- fraud.db # 25 MB SQLite (not committed)
|-- notebooks/
| |-- 01_data_inspection.ipynb # Data inspection
| +-- 02_modeling.ipynb # Feature engineering & ML models
|-- sql/
| |-- 01_velocity.sql # Velocity analysis
| +-- 02_device_concentration.sql # Device concentration analysis
|-- outputs/
| |-- 01_data_inspection.png
| |-- 02_velocity_query.png
| |-- 03_device_concentration.png
| |-- 04_lr_threshold_table.png
| |-- 05_feature_importance.png
| |-- 06_dashboard_screenshot.png
| |-- feature_importance.csv
| +-- threshold_table.csv
|-- dashboard/ # Power BI source file (not committed)
+-- memo/ # One-page insight memo (pending)


## Preliminary Findings (SQL Layer)

Three findings, all honestly reported:

**1. Transaction velocity - NULL result.**

Fraud rate is flat across all time-gap buckets between successive transactions by the same customer:

| Gap bucket | Transactions | Frauds | Fraud rate |
|---|---|---|---|
| Under 1 minute | 26 | 5 | 19.23% |
| 1-60 minutes | 856 | 205 | 23.95% |
| 1-24 hours | 18,096 | 4,406 | 24.35% |
| Over 1 day | 80,375 | 19,219 | 23.91% |

Baseline 23.986%. No velocity signal. Timestamps appear randomly generated rather than drawn from realistic customer activity (80.9% of gaps exceed 1 day - implausible for a real UPI user base).

**2. Device concentration - NULL result by structural construction.**

647 unique customers, 647 unique devices. `Device_ID` is 1:1 with `Customer_ID` by construction - every customer uses exactly one device, every device belongs to exactly one customer. Mule-ring detection has no testable signal on this dataset.

**3. IP_Address - random noise.**

99,998 unique IPs across 100,000 transactions. Only 2 duplicate occurrences. IP cannot function as a behavioral signal.

**Why this matters.** The two strongest signals of production fraud detection - velocity (behavioral timing) and device concentration (network structure) - are both structurally absent from this synthetic dataset. The fraud signal, if any exists, must be in the behavioral columns (`Transaction_Frequency`, `Transaction_Amount_Deviation`, `Days_Since_Last_Transaction`, `amount`, plus encoded categoricals). Day 3's Python model tests this.

## Preliminary Findings (Python Modeling)

Three models, all null. The dataset has no learnable signal in the 43 engineered features.

**Setup.** Numeric: Transaction_Frequency, Transaction_Amount_Deviation, Days_Since_Last_Transaction, amount_log, hour, day_of_week, is_weekend. Categorical (one-hot): Transaction_Type, Payment_Gateway, Merchant_Category, Transaction_Channel, Device_OS, Transaction_Status. 43 features total. Stratified 80/20 split. class_weight='balanced'.

**Logistic regression (linear).** Confusion @ 0.5: TN=7,272, FP=7,931, FN=2,312, TP=2,485. Precision 0.2386, recall 0.5180, F1 0.3267. Accuracy 0.4879 — worse than all-zero baseline (0.7601). Precision equals base rate (0.2399) at every threshold.

| Threshold | Flagged | Precision | Recall | F1 |
|---|---|---|---|---|
| 0.3 | 20,000 (all) | 0.2399 | 1.000 | 0.3869 |
| 0.5 | 10,416 | 0.2386 | 0.518 | 0.3267 |
| 0.7 | 0 | 0.0000 | 0.000 | 0.0000 |

The 0.3 row — flagging every row — produces precision exactly equal to the base rate. The model's ranking ability is nil.

**Group split.** By Customer_ID: 517 train customers, 130 test, overlap 0. Precision 0.2433, recall 0.5919, F1 0.3449. Same null. Not caused by customer memorisation.

**Random forest (nonlinear).** Confusion @ 0.5: TN=8,579, FP=6,624, FN=2,714, TP=2,083. Precision 0.2392, recall 0.4342, F1 0.3085. Same null at the nonlinear model class.

**Feature importance — the false lead.** Top 5 (amount_log 0.19, Transaction_Amount_Deviation 0.19, hour 0.13, day_of_week 0.07, Days_Since_Last_Transaction 0.06) carry 0.64 of total importance, 5.5x uniform baseline. Not signal: amount_log + Transaction_Amount_Deviation are correlated (same underlying quantity, split noise); hour is uniform (4,046-4,351 per hour) but offers 23 split points. The definitive test is precision vs. base rate: 0.2392 vs. 0.2399 — indistinguishable.

**Why this matters.** Three independent signals — velocity (time), device concentration (network), behavioral columns (features) — all null. The synthetic generator drew each row independently. No feature predicts the label. The 24% fraud rate is a label rate, not a learnable target.

## Dashboard

**Screenshot:** [`outputs/06_dashboard_screenshot.png`](outputs/06_dashboard_screenshot.png)

The dashboard visualises the three null results so a reader can verify the finding in ten seconds:

- **Precision vs. Recall across thresholds** — precision stays flat at the base rate (0.2399) while recall falls from 1.0 to 0. Visual proof of no ranking ability.
- **Feature importance vs. uniform baseline** — the top-5 features tower above 1/43, but the subtitle explains why concentration is a Gini artifact, not signal: precision equals base rate (0.2392 vs 0.2399).
- **Fraud rate by hour of day** — 24 bars all at roughly 0.24, no cycle. Uniform distribution visualised.
- **Data quality diagnostic** — 100,000 transactions, 0 missing values, 647 customers, 647 devices (1:1 mapping), 99,998 unique IPs.

The dashboard is a template. On genuine UPI data, the precision-recall chart would show precision climbing steeply with threshold, the feature-importance chart would name real signal-carrying columns, and the hour-of-day chart would show fraud concentrating in low-traffic hours.

## Status

- [x] Data inspection (Nov 3)
- [x] SQL layer - velocity null, device concentration null (Nov 5)
- [x] Python modeling - logistic + random forest, precision = base rate (Day 3)
- [x] Power BI dashboard - built, null results visualised (Day 4)
- [ ] One-page insight memo (Day 5-6)
