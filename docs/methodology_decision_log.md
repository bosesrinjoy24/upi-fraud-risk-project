# Methodology and Decision Log

This document records the principal analytical and engineering decisions made during the project.

## 1. Excluding Transaction Status

**Decision:** Exclude `Transaction_Status` from model predictors.

**Reason:** Completed, failed, and pending statuses describe processing outcomes. They would not be available at the initial transaction-scoring point.

## 2. Excluding Unverified Historical Features

**Decision:** Exclude:

- `Transaction_Frequency`
- `Transaction_Amount_Deviation`
- `Days_Since_Last_Transaction`

**Reason:** Their original computation windows and temporal provenance could not be verified. Including them without verification could introduce leakage or unrealistic availability assumptions.

The exclusion reduces known risks but does not prove that the remaining data is entirely leakage-free.

## 3. Feature Engineering

**Decision:** Derive the following features from the current transaction:

- `amount_log` from `amount` using `log1p`.
- `hour` from the transaction timestamp.
- `day_of_week` from the transaction timestamp.
- `is_weekend` from the day of the week.

**Reason:** These transformations use fields belonging to the current transaction rather than unverified historical aggregates.

## 4. Customer-Grouped Cross-Validation

**Decision:** Use five-fold `StratifiedGroupKFold`, grouped by `Customer_ID`, with shuffling and random state 42.

**Reason:** Grouping prevents a customer's transactions from appearing in both training and validation partitions within the same fold. Stratification aims to preserve class proportions.

`Customer_ID` is not included as a model predictor.

## 5. Out-of-Fold Predictions

**Decision:** Generate out-of-fold predictions for business-cost simulation and model evaluation.

**Reason:** Each transaction is scored by a model that did not train on that transaction. With customer grouping, the corresponding validation customer's transactions are also excluded from that fold's training data.

This provides a more appropriate evaluation than in-sample predictions, subject to the limitations of the dataset and validation design.

## 6. Model Selection

**Decision:** Compare:

- Stratified Dummy Classifier.
- Balanced Logistic Regression with `max_iter=1000`.
- Balanced Random Forest with 200 trees, maximum depth 12, and minimum leaf size 20.

**Reason:** The baseline provides a reference against which trained models can be assessed. Logistic Regression provides a linear benchmark, while Random Forest provides a nonlinear comparison.

## 7. Preprocessing

**Decision:** Use a `ColumnTransformer` with numeric scaling and categorical one-hot encoding.

**Reason:** Preprocessing is fitted within the model pipeline, so transformations are learned from each training fold rather than from the complete dataset.

## 8. Permutation Importance

**Decision:** Calculate Random Forest permutation importance on held-out fold data, using ROC-AUC scoring and five repeats.

**Reason:** Held-out permutation importance provides a fold-specific estimate of how much the fitted model's score changes when a feature is permuted. It does not establish causality.

## 9. Business Cost Simulation

**Decision:** Use out-of-fold Random Forest probabilities with illustrative assumptions of ₹20 per investigation and ₹500 per missed fraud.

**Reason:** Translate threshold decisions into a transparent scenario-based cost comparison.

These values are assumptions, not actual bank operating costs or observed fraud losses.

## 10. Interpretation of Results

**Decision:** Report near-chance ROC-AUC values as a null result.

**Reason:** The trained models do not demonstrate meaningful discrimination over the Dummy baseline. The result is limited to the current synthetic dataset, selected features, and grouped validation design.
