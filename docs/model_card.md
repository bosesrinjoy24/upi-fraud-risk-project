# Data Dictionary

| Column | Type | Business Meaning | Used in ML? | Leakage Risk? |
| :--- | :--- | :--- | :--- | :--- |
| `Transaction_ID` | String | Unique identifier for the transaction. | No | No |
| `Date` | String | Date of transaction (DD/MM/YY). | No (transformed) | No |
| `Time` | String | Time of transaction (12-hr AM/PM). | No (transformed) | No |
| `Merchant_ID` | String | Identifier for the merchant. | No | No |
| `Customer_ID` | String | Identifier for the customer. Used for GroupKFold. | No | No |
| `Device_ID` | String | Identifier for the device. | No | No |
| `Transaction_Type` | Categorical | Purchase, Bill Payment, etc. | Yes | No |
| `Payment_Gateway` | Categorical | The gateway processing the payment. | Yes | No |
| `Transaction_City` | String | City of transaction. | No | No |
| `Transaction_State` | String | State of transaction. | No | No |
| `IP_Address` | String | IP address of the device. | No | No |
| `Transaction_Status`| Categorical | Completed, Failed, Pending. | **NO** | **YES (Removed)** |
| `Device_OS` | Categorical | Android, iOS, Windows, MacOS. | Yes | No |
| `Transaction_Frequency` | Integer | Historical count of customer transactions. | Yes | **High (Unverified)** |
| `Merchant_Category` | Categorical | Category of merchant (e.g., Utilities). | Yes | No |
| `Transaction_Channel` | Categorical | Mobile, Online, In-store. | Yes | No |
| `Transaction_Amount_Deviation` | Float | Deviation from customer's average amount. | Yes | **High (Unverified)** |
| `Days_Since_Last_Transaction` | Integer | Days since the customer's previous transaction. | Yes | **High (Unverified)** |
| `amount` | Float | Transaction amount. | Yes (`amount_log`) | No |
| `fraud` | Integer | Target: 1 = Fraud, 0 = Genuine. | Target | No |