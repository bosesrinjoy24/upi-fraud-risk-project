# Model Card: UPI Fraud Risk Analytics

## 1. Model Overview

**Project:** UPI Fraud Risk Analytics

**Task:** Binary classification of transaction fraud labels.

**Dataset:** 100,000 synthetic UPI transaction records.

**Target:** `fraud` (1 = fraud, 0 = genuine).

**Status:** Research and portfolio evaluation only. Not approved for production use.

## 2. Intended Use

The models are intended to demonstrate:

- Transaction-data validation.
- Leakage-aware feature selection.
- Customer-grouped cross-validation.
- Out-of-fold model evaluation.
- Illustrative threshold-based cost analysis.

They are not intended to authorize, decline, block, or investigate real financial transactions.

## 3. Dataset

| Item | Value |
|---|---:|
| Total transactions | 100,000 |
| Genuine transactions | 76,014 |
| Fraud-labelled transactions | 23,986 |
| Fraud share | 23.986% |
| Missing values in inspected dataset | 0 |

The dataset is synthetic. Its class distribution must not be interpreted as the real-world UPI fraud rate.

## 4. Models Evaluated

| Model | Configuration |
|---|---|
| Dummy Classifier | Stratified baseline |
| Logistic Regression | Balanced class weights, maximum 1,000 iterations |
| Random Forest | 200 trees, maximum depth 12, minimum leaf size 20, balanced class weights |

Preprocessing uses numeric scaling and categorical one-hot encoding within the cross-validation pipeline.

## 5. Evaluation Design

- Five-fold `StratifiedGroupKFold`.
- Grouping variable: `Customer_ID`.
- Shuffling enabled.
- Random state: 42.
- Metrics are aggregated from out-of-fold predictions.
- Random Forest permutation importance is calculated on held-out folds.

## 6. Out-of-Fold Results

| Metric | Dummy | Logistic Regression | Random Forest |
|---|---:|---:|---:|
| ROC-AUC | 0.498613 | 0.500590 | 0.501776 |
| Average Precision | 0.239359 | 0.241202 | 0.241436 |
| Precision | 0.237742 | 0.239949 | 0.240824 |
| Recall | 0.236721 | 0.511090 | 0.378596 |
| F1 | 0.237231 | 0.326576 | 0.294388 |
| Brier Score | 0.365130 | 0.250042 | 0.247696 |

Precision, recall, and F1 are threshold-dependent results at the pipeline's 0.5 classification threshold. ROC-AUC and Average Precision assess ranking performance.

The trained models remain close to chance-level ROC-AUC. Their results do not support a claim of useful fraud discrimination.

The Random Forest mean out-of-fold predicted probability is 0.495102, compared with the observed fraud prevalence of 0.239860. Its probability range is 0.416947 to 0.572974. Its Brier score (0.247696) is worse than the approximately 0.182327 constant-prevalence reference.

## 7. Feature Set

Numeric:

- `amount_log`
- `hour`
- `day_of_week`
- `is_weekend`

Categorical:

- `Transaction_Type`
- `Payment_Gateway`
- `Merchant_Category`
- `Transaction_Channel`
- `Device_OS`

`Customer_ID` is used only for cross-validation grouping. Unverified historical features and post-transaction status are excluded.

## 8. Cost Simulation

Illustrative assumptions:

- ₹20 per investigated transaction.
- ₹500 per missed fraudulent transaction.

At threshold 0.5, the simulation reports total cost of ₹8,206,660. These assumptions are not measured bank costs.

## 9. Limitations and Risks

- Synthetic data may not represent actual UPI transaction behaviour.
- The observed fraud share is not a real-world prevalence estimate.
- Feature provenance and operational availability have not been independently verified.
- Near-chance discrimination limits practical usefulness.
- The cost assumptions are illustrative.
- No production monitoring, live shadow testing, or operational validation is established by this project.

## 10. Ethical and Operational Considerations

These models must not be used to make real financial decisions. A real deployment would require representative data, validated labels, feature-lineage controls, fairness analysis, calibration and threshold studies, security review, human oversight, and ongoing monitoring.

## 11. Reproducibility

The source code, SQL investigations, tests, and generated outputs are maintained in the project repository.

The principal evaluation outputs are:

- `outputs/model_metrics.csv`
- `outputs/fold_metrics.csv`
- `outputs/oof_predictions.csv`
- `outputs/permutation_importance.csv`
- `outputs/cost_simulation.csv`
