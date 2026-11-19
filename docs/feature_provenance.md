# Feature Provenance and Leakage Risk Assessment

## 1. Purpose

This document records which dataset fields are used for prediction, which are excluded, and what is known about their availability at the intended scoring time.

The dataset's original feature-generation process is not independently verified. Therefore, availability claims are treated cautiously.

## 2. Feature Assessment

| Feature | Model use | Prediction-time assessment | Decision |
|---|---|---|---|
| `amount` | Transformed to `amount_log` | Current transaction amount; expected to be available before authorization | Included |
| `Date`, `Time` | Transformed to `hour`, `day_of_week`, `is_weekend` | Current transaction timestamp; expected to be available | Included as derived features |
| `Transaction_Type` | Yes | Expected to be known from the transaction request | Included |
| `Payment_Gateway` | Yes | Expected to be known during routing or processing | Included |
| `Merchant_Category` | Yes | Expected to be available from merchant metadata | Included |
| `Transaction_Channel` | Yes | Expected to be known from the transaction channel | Included |
| `Device_OS` | Yes | Expected to be available from device metadata | Included |
| `Transaction_Frequency` | No | Historical computation and observation window are unverified | Excluded |
| `Transaction_Amount_Deviation` | No | Historical computation and reference window are unverified | Excluded |
| `Days_Since_Last_Transaction` | No | Historical computation and event-time availability are unverified | Excluded |
| `Transaction_Status` | No | Post-processing outcome; unavailable at initial scoring | Excluded |
| `Customer_ID` | No | Used only for grouped cross-validation | Excluded as predictor |
| Other identifiers and location fields | No | Not part of the selected predictor set | Excluded |

## 3. Selected Model Features

Numeric features:

- `amount_log`
- `hour`
- `day_of_week`
- `is_weekend`

Categorical features:

- `Transaction_Type`
- `Payment_Gateway`
- `Merchant_Category`
- `Transaction_Channel`
- `Device_OS`

## 4. Leakage Risk Interpretation

The three historical features are excluded because their computation and temporal provenance cannot be established from the available documentation.

`Transaction_Status` is excluded because it represents a transaction outcome that would not be available at the initial scoring point.

`Customer_ID` is used as a grouping variable to prevent customers from appearing in both the training and validation partitions of a fold.

## 5. Conclusion

These decisions reduce identifiable leakage risks. They do not establish that the complete dataset-generation process is leakage-free or that every included field has been independently verified for operational availability.

Before real-world deployment, each included feature would require source-system, event-time, and data-lineage verification.
