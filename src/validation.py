import numpy as np
import pandas as pd


def validate_transactions(df: pd.DataFrame) -> bool:
    """Validate the transaction dataset before feature engineering and modelling.

    Raises:
        TypeError: If the input is not a pandas DataFrame.
        ValueError: If one or more data-quality checks fail.

    Returns:
        bool: True when all required validation checks pass.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    errors = []
    warnings = []

    # 1. Check that the dataset is not empty.
    if df.empty:
        raise ValueError("Transaction dataset is empty.")

    # 2. Check the minimum columns required by the pipeline.
    required_cols = {
        "Transaction_ID",
        "Customer_ID",
        "Date",
        "Time",
        "amount",
        "fraud",
        "Transaction_Type",
        "Payment_Gateway",
        "Merchant_Category",
        "Transaction_Channel",
        "Device_OS",
    }

    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

    # 3. Validate transaction identifiers.
    for col in ["Transaction_ID", "Customer_ID"]:
        values = df[col].astype("string").str.strip()

        if values.isna().any() or values.eq("").fillna(False).any():
            errors.append(f"Missing or blank values found in '{col}'.")

    transaction_ids = (
        df["Transaction_ID"]
        .astype("string")
        .str.strip()
    )

    if transaction_ids.duplicated().any():
        errors.append("Duplicate Transaction_IDs found.")

    # 4. Validate transaction amounts.
    amounts = pd.to_numeric(df["amount"], errors="coerce")

    if amounts.isna().any():
        errors.append("Missing or non-numeric values found in 'amount'.")
    elif not np.isfinite(amounts.to_numpy(dtype=float)).all():
        errors.append("Non-finite values found in 'amount'.")
    elif (amounts <= 0).any():
        errors.append("Found transaction amounts <= 0.")

    # 5. Validate the fraud target.
    fraud = pd.to_numeric(df["fraud"], errors="coerce")

    if fraud.isna().any():
        errors.append("Missing or non-numeric values found in 'fraud'.")
    elif not fraud.isin([0, 1]).all():
        errors.append("Invalid 'fraud' labels found. Only 0 and 1 allowed.")

    # 6. Validate date and time values.
    datetime_values = (
        df["Date"].astype("string").str.strip()
        + " "
        + df["Time"].astype("string").str.strip()
    )

    parsed_dates = pd.to_datetime(
        datetime_values,
        format="%d/%m/%y %I:%M:%S %p",
        errors="coerce"
    )

    if parsed_dates.isna().any():
        invalid_count = int(parsed_dates.isna().sum())
        errors.append(
            f"{invalid_count} invalid or missing Date/Time values found."
        )

    # 7. Validate categorical model inputs.
    categorical_cols = [
        "Transaction_Type",
        "Payment_Gateway",
        "Merchant_Category",
        "Transaction_Channel",
        "Device_OS",
    ]

    for col in categorical_cols:
        values = df[col].astype("string").str.strip()

        if values.isna().any() or values.eq("").fillna(False).any():
            errors.append(
                f"Missing or blank categorical values found in '{col}'."
            )

    # 8. Report unexpected transaction types as warnings.
    valid_types = {
        "Purchase",
        "Bill Payment",
        "Subscription",
        "Bank Transfer",
        "Investment",
        "Refund",
        "Other",
    }

    actual_types = set(
        df["Transaction_Type"].dropna().astype(str).str.strip().unique()
    )

    unexpected_types = actual_types - valid_types

    if unexpected_types:
        warnings.append(
            f"Unexpected Transaction_Type values: "
            f"{sorted(unexpected_types)}"
        )

    # 9. Print validation report.
    print("\n--- DATA VALIDATION REPORT ---")

    for warning in warnings:
        print(f"[WARNING] {warning}")

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")

        raise ValueError("\n".join(errors))

    print("[OK] All data validation checks passed.")
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")

    return True
