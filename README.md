# BFSI UPI Fraud Risk Profiling

**Business question:** Which transaction patterns in a UPI payment flow are most predictive of fraud, and what is the precision-recall trade-off at different risk thresholds?

**Decision owner:** A fraud risk team lead at a fintech or payment service provider.

## TL;DR

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
| Python modeling | pandas, scikit-learn - logistic regression, random forest, precision-recall | Next (Day 3) |
| Dashboard | Power BI Desktop | Pending |
| Memo | One-page insight memo (PDF) | Pending |

## Repository Map

```
upi-fraud-risk-project/
|-- README.md                       # This file
|-- .gitignore                      # Excludes *.csv, *.db, *.db-journal, checkpoints
|-- data/
|   |-- README.md                   # Source + synthetic caveat
|   |-- UPI_FRAUD_100K.csv          # 25.37 MB (not committed - see .gitignore)
|   +-- fraud.db                    # 25 MB SQLite (not committed - rebuild from CSV)
|-- notebooks/
|   +-- 01_data_inspection.ipynb    # Data inspection: shape, columns, dtypes, fraud distribution
|-- sql/
|   |-- 01_velocity.sql             # Velocity analysis (3 steps + comments)
|   +-- 02_device_concentration.sql # Device concentration analysis (3 steps + comments)
|-- outputs/
|   |-- 01_data_inspection.png      # Data inspection screenshot
|   |-- 02_velocity_query.png       # Velocity analysis screenshot
|   +-- 03_device_concentration.png # Device concentration screenshot
|-- dashboard/                      # (pending)
+-- memo/                           # (pending)
```

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

Both SQL query files are preserved in `sql/` with detailed comments - including the two date-parsing traps caught during development - for direct application to real UPI data, where velocity and device concentration are strong signals.

## Status

- [x] Data inspection (Nov 3)
- [x] SQL layer - import verification, velocity, device concentration (Nov 5)
- [ ] Python modeling (Day 3 - next)
- [ ] Power BI dashboard
- [ ] One-page insight memo
