# Technical Architecture

## 1. Project Overview

This project evaluates fraud-risk classification using a 100,000-row synthetic UPI transaction dataset. The workflow includes data validation, feature engineering, grouped cross-validation, model evaluation, business-cost simulation, exploratory analysis, and SQL investigations.

## 2. End-to-End Machine Learning Pipeline

```mermaid
flowchart TD
    A[UPI Transaction CSV] --> B[data_loader.py]
    B --> C[validation.py]
    C -->|Validation fails| D[Stop pipeline]
    C -->|Validation passes| E[features.py]
    E --> F[Feature selection]
    F --> G[ColumnTransformer preprocessing]
    G --> H[StratifiedGroupKFold by Customer_ID]
    H --> I[Dummy, Logistic Regression, Random Forest]
    I --> J[Out-of-Fold predictions]
    I --> K[Fold metrics]
    I --> L[Permutation importance]
    J --> M[cost_simulator.py]
    J --> N[Aggregated model metrics]
    M --> O[cost_simulation.csv]
    K --> P[fold_metrics.csv]
    L --> Q[permutation_importance.csv]
    N --> R[model_metrics.csv]
    J --> S[oof_predictions.csv]
```

## 3. Supporting Analytical Workflows

### Exploratory Data Analysis

- `scripts/eda_analysis.py` generates descriptive summaries and statistical tests.
- Results are saved under `outputs/`.
- Effect sizes are considered alongside p-values.

### SQL Investigations

- `sql/01_velocity.sql` examines time gaps between consecutive transactions for each customer.
- `sql/02_device_concentration.sql` examines device and IP address reuse.
- These are descriptive investigations, not proof of fraud or causal relationships.

## 4. Model Evaluation Design

- Five-fold `StratifiedGroupKFold` cross-validation.
- `Customer_ID` is the grouping variable, not a model predictor.
- Each transaction receives an out-of-fold prediction from a model that did not train on that transaction.
- Logistic Regression and Random Forest are compared against a Dummy Classifier.
- Random Forest permutation importance is calculated on held-out folds.

## 5. Business Cost Simulation

The cost simulator evaluates threshold-based decisions using out-of-fold probabilities.

Illustrative assumptions:

- Investigation cost: ₹20 per flagged transaction.
- Missed-fraud cost: ₹500 per missed fraudulent transaction.

Formula:

`Total_Cost = (Flagged ₹ Investigation_Cost) + (False_Negatives ₹ Missed_Fraud_Cost)`

These are scenario assumptions, not measured bank losses. The generated `outputs/cost_simulation.csv` uses the field `Total_Cost`.

## 6. Important Limitations

- The dataset is synthetic and does not establish real-world UPI fraud performance.
- Three historical features with unverified provenance are excluded from the model.
- Near-chance model discrimination must be reported honestly.
- The evaluation reduces known leakage risks but does not prove that every possible source of leakage has been eliminated.
