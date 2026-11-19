import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))  # noqa: E402

from src.features import engineer_features, get_feature_columns  # noqa: E402


def sample_df():
    return pd.DataFrame({
        "Date": ["12/02/22", "13/02/22", "14/02/22"],
        "Time": ["08:20:00 AM", "09:00:00 AM", "10:00:00 AM"],
        "amount": [100.0, 200.0, 150.0],
        "Transaction_Type": ["Purchase", "Purchase", "Refund"],
        "Payment_Gateway": ["A", "A", "B"],
        "Merchant_Category": ["Retail", "Retail", "Services"],
        "Transaction_Channel": ["Mobile", "Mobile", "Online"],
        "Device_OS": ["Android", "Android", "iOS"],
        "Transaction_Frequency": [0, 1, 0],
        "Transaction_Amount_Deviation": [10.0, 15.0, -5.0],
        "Days_Since_Last_Transaction": [10, 1, 5],
    })


def test_engineer_features_creates_expected_columns():
    df = sample_df()

    result = engineer_features(df)

    expected_columns = [
        "amount_log",
        "hour",
        "day_of_week",
        "is_weekend",
    ]

    for column in expected_columns:
        assert column in result.columns


def test_engineer_features_calculates_log_amount_correctly():
    df = sample_df()

    result = engineer_features(df)

    expected = np.log1p(df["amount"])

    pd.testing.assert_series_equal(
        result["amount_log"],
        expected.rename("amount_log"),
    )


def test_engineer_features_extracts_hour_correctly():
    df = sample_df()

    result = engineer_features(df)

    assert result["hour"].tolist() == [8, 9, 10]


def test_engineer_features_extracts_day_of_week_correctly():
    df = sample_df()

    result = engineer_features(df)

    # Monday = 0, Sunday = 6
    assert result["day_of_week"].tolist() == [5, 6, 0]


def test_engineer_features_identifies_weekends_correctly():
    df = sample_df()

    result = engineer_features(df)

    assert result["is_weekend"].tolist() == [1, 1, 0]


def test_engineer_features_does_not_modify_original_dataframe():
    df = sample_df()
    original_df = df.copy(deep=True)

    engineer_features(df)

    pd.testing.assert_frame_equal(df, original_df)


def test_get_feature_columns_excludes_unverified_historical_features():
    num_cols, cat_cols = get_feature_columns()

    excluded_features = {
        "Transaction_Frequency",
        "Transaction_Amount_Deviation",
        "Days_Since_Last_Transaction",
    }

    assert excluded_features.isdisjoint(num_cols)
    assert excluded_features.isdisjoint(cat_cols)


def test_get_feature_columns_returns_expected_features():
    num_cols, cat_cols = get_feature_columns()

    assert num_cols == [
        "amount_log",
        "hour",
        "day_of_week",
        "is_weekend",
    ]

    assert cat_cols == [
        "Transaction_Type",
        "Payment_Gateway",
        "Merchant_Category",
        "Transaction_Channel",
        "Device_OS",
    ]
