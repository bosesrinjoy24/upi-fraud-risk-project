# Feature Provenance & Leakage Risk Assessment

This document outlines the availability of each feature at the exact moment a real-time fraud prediction is made.

| Feature | Type | Available at Prediction Time? | Leakage Risk / Notes |
| :--- | :--- | :--- | :--- |
| `Transaction_Frequency` | Historical | **Unverified** | **HIGH RISK.** Pre-computed in dataset. If calculated using future daily transactions, this is leakage. |
| `Transaction_Amount_Deviation` | Historical | **Unverified** | **HIGH RISK.** Pre-computed. May use the current transaction to calculate deviation. |
| `Days_Since_Last_Transaction` | Historical | **Unverified** | **HIGH RISK.** Pre-computed. Hard to verify if it strictly uses past timestamps. |
| `amount_log` | Transaction | Yes | Safe. Derived directly from the current transaction amount (`np.log1p`). |
| `hour` | Transaction | Yes | Safe. Derived from the current timestamp. |
| `day_of_week` | Transaction | Yes | Safe. Derived from the current timestamp. |
| `is_weekend` | Transaction | Yes | Safe. Derived from the current timestamp. |
| `Transaction_Type` | Transaction | Yes | Safe. Known at time of swipe. |
| `Payment_Gateway` | Transaction | Yes | Safe. Known at time of swipe. |
| `Merchant_Category` | Transaction | Yes | Safe. Known at time of swipe. |
| `Transaction_Channel` | Transaction | Yes | Safe. Known at time of swipe. |
| `Device_OS` | Transaction | Yes | Safe. Known at time of swipe. |
| `Transaction_Status` | Post-Trans | **NO** | **REMOVED.** (Completed/Failed/Pending) is only known after processing. |

**Conclusion:** Due to the limitations of the pre-computed dataset, historical features cannot be independently verified for point-in-time accuracy. This limits the model's real-world validity and must be disclosed in all reporting.