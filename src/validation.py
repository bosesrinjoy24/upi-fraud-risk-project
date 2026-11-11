import pandas as pd
import numpy as np

def validate_transactions(df: pd.DataFrame) -> bool:
    errors = []
    warnings = []

    required_cols = {
        'Transaction_ID', 'Date', 'Time', 'Merchant_ID', 'Customer_ID', 
        'Device_ID', 'Transaction_Type', 'Payment_Gateway', 'Transaction_City', 
        'Transaction_State', 'IP_Address', 'Transaction_Status', 'Device_OS', 
        'Transaction_Frequency', 'Merchant_Category', 'Transaction_Channel', 
        'Transaction_Amount_Deviation', 'Days_Since_Last_Transaction', 
        'amount', 'fraud'
    }
    
    # 1. Check required columns
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # 2. Target validation
    if not df['fraud'].isin([0, 1]).all():
        errors.append("Invalid 'fraud' labels found. Only 0 and 1 allowed.")
    
    # 3. Numeric Validation
    if (df['amount'] <= 0).any():
        errors.append("Found transaction amounts <= 0.")
    if df['amount'].isnull().any():
        errors.append("Null values found in 'amount' column.")
    
    # 4. Categorical Validation (Example: Transaction_Type)
    valid_types = ['Purchase', 'Bill Payment', 'Subscription', 'Bank Transfer', 'Investment', 'Refund', 'Other']
    unexpected_types = df[~df['Transaction_Type'].isin(valid_types)]['Transaction_Type'].unique()
    if len(unexpected_types) > 0:
        warnings.append(f"Unexpected Transaction_Types found: {unexpected_types}")

    # 5. Duplicate IDs
    if df['Transaction_ID'].duplicated().any():
        errors.append("Duplicate Transaction_IDs found.")

    # 6. Identifier completeness
    for col in ['Customer_ID', 'Device_ID', 'Transaction_ID']:
        if df[col].isnull().any():
            errors.append(f"Null values found in identifier column '{col}'.")

    # Report
    print("--- DATA VALIDATION REPORT ---")
    if warnings:
        for w in warnings: print(f"[WARNING] {w}")
    if errors:
        for e in errors: print(f"[ERROR] {e}")
        # The fix: raise the actual joined error string, not a generic summary
        raise ValueError("\n".join(errors))
    
    print("[OK] All data validation checks passed.")
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    return True