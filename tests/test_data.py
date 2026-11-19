import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))  # noqa: E402
from src.validation import validate_transactions  # noqa: E402


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Transaction_ID": ["T1", "T2", "T3"],
        "Date": ["12/02/22", "13/02/22", "14/02/22"],
        "Time": ["08:20:00 AM", "09:00:00 AM", "10:00:00 AM"],
        "Merchant_ID": ["M1", "M1", "M2"],
        "Customer_ID": ["C1", "C1", "C2"],
        "Device_ID": ["D1", "D1", "D2"],
        "Transaction_Type": ["Purchase", "Purchase", "Refund"],
        "Payment_Gateway": ["A", "A", "B"],
        "Transaction_City": ["X", "X", "Y"],
        "Transaction_State": ["S1", "S1", "S2"],
        "IP_Address": ["1.1.1.1", "1.1.1.2", "2.2.2.2"],
        "Transaction_Status": ["Completed", "Completed", "Pending"],
        "Device_OS": ["Android", "Android", "iOS"],
        "Transaction_Frequency": [0, 1, 0],
        "Merchant_Category": ["Retail", "Retail", "Services"],
        "Transaction_Channel": ["Mobile", "Mobile", "Online"],
        "Transaction_Amount_Deviation": [10.0, 15.0, -5.0],
        "Days_Since_Last_Transaction": [10, 1, 5],
        "amount": [100.0, 200.0, 150.0],
        "fraud": [0, 1, 0],
    })


def test_validation_passes_on_valid_data(sample_df):
    assert validate_transactions(sample_df) is True


def test_validation_catches_missing_columns(sample_df):
    broken_df = sample_df.drop(columns=["amount"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_transactions(broken_df)


def test_validation_catches_invalid_fraud_labels(sample_df):
    sample_df.loc[0, "fraud"] = 2
    with pytest.raises(ValueError, match="Invalid 'fraud' labels"):
        validate_transactions(sample_df)


def test_validation_catches_negative_amounts(sample_df):
    sample_df.loc[0, "amount"] = -10.0
    with pytest.raises(ValueError, match="Found transaction amounts <= 0"):
        validate_transactions(sample_df)


def test_validation_rejects_empty_dataset(sample_df):
    empty_df = sample_df.iloc[0:0].copy()

    with pytest.raises(ValueError, match="empty"):
        validate_transactions(empty_df)


def test_validation_catches_duplicate_transaction_ids(sample_df):
    sample_df.loc[1, "Transaction_ID"] = "T1"

    with pytest.raises(ValueError, match="Duplicate Transaction_IDs"):
        validate_transactions(sample_df)


def test_validation_catches_missing_customer_id(sample_df):
    sample_df.loc[0, "Customer_ID"] = None

    with pytest.raises(ValueError, match="Customer_ID"):
        validate_transactions(sample_df)


def test_validation_catches_blank_device_or_identifier(sample_df):
    sample_df.loc[0, "Transaction_ID"] = "   "

    with pytest.raises(ValueError, match="Transaction_ID"):
        validate_transactions(sample_df)


def test_validation_catches_non_numeric_amount(sample_df):
    sample_df["amount"] = sample_df["amount"].astype(object)
    sample_df.loc[0, "amount"] = "invalid"

    with pytest.raises(ValueError, match="non-numeric"):
        validate_transactions(sample_df)


def test_validation_catches_infinite_amount(sample_df):
    sample_df.loc[0, "amount"] = float("inf")

    with pytest.raises(ValueError, match="Non-finite"):
        validate_transactions(sample_df)


def test_validation_catches_missing_amount(sample_df):
    sample_df.loc[0, "amount"] = None

    with pytest.raises(ValueError, match="Missing or non-numeric"):
        validate_transactions(sample_df)


def test_validation_catches_invalid_datetime(sample_df):
    sample_df.loc[0, "Date"] = "invalid-date"

    with pytest.raises(ValueError, match="invalid or missing Date/Time"):
        validate_transactions(sample_df)


def test_validation_catches_missing_categorical_value(sample_df):
    sample_df.loc[0, "Payment_Gateway"] = None

    with pytest.raises(ValueError, match="Payment_Gateway"):
        validate_transactions(sample_df)


def test_validation_accepts_data_without_unverified_historical_features(
    sample_df
):
    historical_cols = [
        "Transaction_Frequency",
        "Transaction_Amount_Deviation",
        "Days_Since_Last_Transaction",
    ]

    reduced_df = sample_df.drop(columns=historical_cols)

    assert validate_transactions(reduced_df) is True


def test_validation_catches_duplicate_transaction_ids_with_whitespace(
    sample_df
):
    sample_df.loc[1, "Transaction_ID"] = " T1 "

    with pytest.raises(ValueError, match="Duplicate Transaction_IDs"):
        validate_transactions(sample_df)
