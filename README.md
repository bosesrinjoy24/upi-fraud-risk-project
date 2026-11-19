# UPI Fraud Risk Analytics

An end-to-end fraud risk analytics project using 100,000 synthetic UPI transactions. The project evaluates transaction-level fraud patterns, leakage-safe machine learning, grouped cross-validation, and illustrative business-cost trade-offs.

## Business Question

Which transaction characteristics help distinguish fraudulent UPI transactions, and what are the precision-recall and investigation-cost trade-offs at different risk thresholds?

**Decision maker:** Fraud risk team lead at a fintech or payment service provider.

## Dataset

- Source: [Kaggle - UPI Fraud Detection](https://www.kaggle.com/datasets/sameerbhatt12/upi-fraud-detection)
- Size: 100,000 rows and 20 columns
- Target: `fraud` (0 = genuine, 1 = fraudulent)
- Genuine transactions: 76,014
- Fraudulent transactions: 23,986
- Fraud prevalence: 23.986%

**Important:** The dataset is synthetic. Its fraud prevalence and patterns should not be interpreted as representative of real-world UPI traffic or production fraud rates.

The source dataset is not committed to this repository.

## Project Workflow

1. Data loading and validation
2. Exploratory data analysis and statistical testing
3. SQL-based transaction velocity and device/IP analysis
4. Feature engineering and leakage-safe preprocessing
5. Five-fold Stratified Group Cross-Validation
6. Dummy, Logistic Regression, and Random Forest model evaluation
7. Out-of-fold prediction analysis
8. Permutation feature importance
9. Business-cost simulation and threshold sensitivity analysis
10. Automated testing and Power BI reporting

## Methodology

- Data validation checks the dataset before processing.
- Preprocessing is performed through scikit-learn pipelines to prevent training/test leakage.
- Grouped cross-validation uses `StratifiedGroupKFold` with five folds and customer grouping.
- Historical features with unverified provenance are excluded.
- `Transaction_Status` is excluded because final transaction status would not be available at the intended scoring point.
- Out-of-fold predictions are used for aggregated model evaluation and cost simulation.

## Model Performance

Aggregated out-of-fold results:

| Model | ROC-AUC | Average Precision | Precision | Recall | F1 | Brier Score |
|---|---:|---:|---:|---:|---:|---:|
| Dummy | 0.498613 | 0.239359 | 0.237742 | 0.236721 | 0.237231 | 0.365130 |
| Logistic Regression | 0.500590 | 0.241202 | 0.239949 | 0.511090 | 0.326576 | 0.250042 |
| Random Forest | 0.501776 | 0.241436 | 0.240824 | 0.378596 | 0.294388 | 0.247696 |

**Interpretation:** Both trained models have ROC-AUC values close to 0.50. They show little ability to discriminate between fraudulent and genuine transactions on this dataset. The results do not support deploying either model as an effective fraud detector.

The Random Forest Brier score is also worse than the constant-prevalence reference, so its predicted probabilities should not be treated as reliable calibrated risk estimates.

## Business Cost Simulation

The project evaluates multiple risk thresholds under illustrative investigation and missed-fraud cost assumptions.

Selected baseline results:

| Threshold | Flagged Transactions | Detection Rate | Investigation Workload | Total Cost |
|---:|---:|---:|---:|---:|
| 0.1 | 100,000 | 100.00% | 100.00% | INR 2,000,000 |
| 0.3 | 100,000 | 100.00% | 100.00% | INR 2,000,000 |
| 0.5 | 37,708 | 37.86% | 37.71% | INR 8,206,660 |
| 0.7 | 0 | 0.00% | 0.00% | INR 11,993,000 |

These costs are illustrative simulation assumptions, not observed bank losses or real operational costs. The results demonstrate the trade-off between investigation workload and missed fraud under the current model's weak discrimination.

## SQL Analysis

The SQL analysis examines transaction time gaps, device reuse, and IP reuse.

- Transaction velocity is examined across time-gap buckets.
- The velocity analysis includes 99,353 transactions with an eligible preceding customer transaction.
- The top device and customer reuse results do not establish meaningful fraud concentration.
- Two IP addresses are shared by pairs of customers in the dataset.

Device and IP reuse are descriptive investigation signals, not proof of fraudulent activity.

## Power BI Dashboard

The Power BI report contains five pages:

1. Executive Overview
2. Fraud Patterns
3. Device Risk
4. Model Performance
5. Business Cost

The dashboard is built for Power BI Desktop. The `.pbix` file is excluded from Git by the current ignore rules.

## Repository Structure

```text
upi-fraud-risk-project/
|-- README.md
|-- requirements.txt
|-- .github/
|   |-- workflows/
|       |-- ci.yml
|-- src/
|-- scripts/
|-- tests/
|-- notebooks/
|-- sql/
|-- data/
|-- outputs/
|-- docs/
|-- dashboard/
|-- memo/
```

## Generated Outputs

The pipeline generates:

- `model_metrics.csv`
- `fold_metrics.csv`
- `oof_predictions.csv`
- `cost_simulation.csv`
- `permutation_importance.csv`
- `eda_summary.csv`
- `statistical_tests.csv`

## Documentation

The `docs/` directory contains:

- Architecture diagram
- Data dictionary
- Feature provenance
- Methodology and decision log
- Model card
- Limitations and responsible-use notes
- Dashboard guide

## Installation and Execution

Requirements: Python 3.14 or a compatible environment supporting the pinned dependencies.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Place the source dataset at:

```text
data/UPI_FRAUD_100K.csv
```

Run the complete pipeline:

```bash
python scripts/run_pipeline.py
```

Run automated tests:

```bash
python -m pytest tests/ -v
```

Check dependency consistency:

```bash
python -m pip check
```

## Testing and CI

The project includes automated tests for data validation, feature engineering, modeling, and cost simulation.

GitHub Actions runs dependency installation, dependency checks, and the pytest suite on pushes and pull requests targeting `main`.

Latest local test result: **40 passed, 1 non-blocking third-party warning.**

## Limitations

- The dataset is synthetic and has a high fraud prevalence.
- Model discrimination is close to chance level.
- Model probabilities are not suitable for production risk decisions.
- Cost assumptions are illustrative.
- Device/IP reuse does not establish fraud.
- Results should not be generalized to real-world UPI fraud without representative, independently validated data.

## Project Status

The end-to-end analytics pipeline, SQL analyses, automated tests, documentation, business-cost simulation, and Power BI dashboard have been built.

The key analytical finding is that the current synthetic dataset does not provide sufficient predictive signal for effective fraud classification.

This project demonstrates an auditable analytical workflow and transparent reporting of negative results; it does not claim to deliver a production-ready fraud detection model.