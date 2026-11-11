# Methodology & Decision Log

This document records the key analytical decisions made during the development of this project.

### 1. Excluding `Transaction_Status`
- **Decision:** Removed from features.
- **Reason:** It is a post-transaction metric. In a real-time fraud system, the status is unknown at the moment of scoring. Including it causes data leakage and inflates model performance.

### 2. Feature Provenance & Historical Leakage
- **Decision:** Flagged `Transaction_Frequency`, `Transaction_Amount_Deviation`, and `Days_Since_Last_Transaction` as high-risk for leakage.
- **Reason:** The Kaggle dataset pre-computed these. If they use future data (e.g., total daily frequency), they leak future information. Because we cannot recalculate them from raw timestamps, we documented the risk in `feature_provenance.md`.

### 3. Out-of-Fold (OOF) Predictions
- **Decision:** Used OOF predictions for cost simulation, not in-sample predictions.
- **Reason:** Using a model to predict on its own training data yields artificially high performance (memorization). OOF ensures every transaction is scored by a model that never saw it during training, giving an honest business cost estimate.

### 4. StratifiedGroupKFold
- **Decision:** Grouped cross-validation by `Customer_ID`.
- **Reason:** A standard `train_test_split` places the same customer in both train and test sets, causing the model to memorize customer behavior. Grouping ensures we evaluate the model's ability to predict fraud on unseen customers.