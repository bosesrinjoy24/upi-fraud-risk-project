# Data Dictionary

This document describes the 20 columns in the inspected transaction dataset and their roles in the project.

| Column | Data type | Meaning / role | Model use |
|---|---|---|---|
| `Transaction_ID` | String | Transaction identifier | No |
| `Date` | String | Transaction date, DD/MM/YY | Derived features |
| `Time` | String | Transaction time, 12-hour AM/PM | Derived features |
| `Merchant_ID` | String | Merchant identifier | No |
| `Customer_ID` | String | Customer identifier; used for grouped cross-validation | Group only |
| `Device_ID` | String | Device identifier | No |
| `Transaction_Type` | String | Transaction category/type | Yes |
| `Payment_Gateway` | String | Payment gateway label | Yes |
| `Transaction_City` | String | Transaction city | No |
| `Transaction_State` | String | Transaction state | No |
| `IP_Address` | String | Transaction IP address | No |
| `Transaction_Status` | String | Processing outcome/status | No; post-transaction |
| `Device_OS` | String | Device operating system | Yes |
| `Transaction_Frequency` | Integer | Historical transaction-frequency field | No; provenance unverified |
| `Merchant_Category` | String | Merchant category | Yes |
| `Transaction_Channel` | String | Transaction channel | Yes |
| `Transaction_Amount_Deviation` | Float | Historical amount-deviation field | No; provenance unverified |
| `Days_Since_Last_Transaction` | Integer | Historical time-since-previous-transaction field | No; provenance unverified |
| `amount` | Float | Transaction amount | Yes, transformed |
| `fraud` | Integer | Target label: 1 = fraud, 0 = genuine | Target |

## Derived Features

| Derived feature | Source | Transformation |
|---|---|---|
| `amount_log` | `amount` | `log1p(amount)` |
| `hour` | `Date`, `Time` | Hour extracted from parsed timestamp |
| `day_of_week` | `Date`, `Time` | Day of week extracted from parsed timestamp |
| `is_weekend` | `day_of_week` | 1 when day is Saturday or Sunday; otherwise 0 |

## Important Notes

- `Customer_ID` is not a model predictor.
- `fraud` is the target, not a predictor.
- `Transaction_Status` is excluded because it is a post-transaction outcome.
- The three historical fields are excluded because their computation and temporal provenance are unverified.
- Inclusion of a field in the model does not independently prove its real-world availability. Operational data lineage must be verified separately.
