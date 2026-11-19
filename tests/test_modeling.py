import numpy as np
import pandas as pd
import pytest

from src.modeling import train_and_evaluate_oof


@pytest.fixture
def modeling_df():
    rng = np.random.default_rng(42)
    rows = []

    for customer in range(50):
        for transaction in range(4):
            rows.append({
                "Customer_ID": f"C{customer}",
                "amount_log": float(rng.uniform(1, 8)),
                "Transaction_Type": (
                    "P2P" if transaction % 2 == 0 else "Merchant"
                ),
                "fraud": transaction % 2,
            })

    return pd.DataFrame(rows)


def test_modeling_returns_complete_oof_predictions(modeling_df):
    agg, folds, oof_rf, y_true, importance = (
        train_and_evaluate_oof(
            modeling_df,
            ["amount_log"],
            ["Transaction_Type"],
            "Customer_ID",
        )
    )

    assert len(agg) == 3
    assert len(folds) == 15
    assert len(oof_rf) == len(modeling_df)
    assert len(y_true) == len(modeling_df)
    assert np.isfinite(oof_rf).all()
    assert ((oof_rf >= 0) & (oof_rf <= 1)).all()

    assert set(agg["Model"]) == {"Dummy", "LR", "RF"}
    assert set(folds["Model"]) == {"Dummy", "LR", "RF"}

    assert agg["Total_Rows"].eq(len(modeling_df)).all()
    assert folds["Test_Rows"].sum() == 3 * len(modeling_df)

    assert len(importance) == 10
    assert set(importance["Feature"]) == {
        "amount_log",
        "Transaction_Type",
    }


def test_modeling_rejects_empty_dataframe():
    with pytest.raises(ValueError, match="empty"):
        train_and_evaluate_oof(
            pd.DataFrame(),
            ["amount_log"],
            [],
            "Customer_ID",
        )


def test_modeling_rejects_single_class_target(modeling_df):
    modeling_df["fraud"] = 0

    with pytest.raises(ValueError, match="both binary classes"):
        train_and_evaluate_oof(
            modeling_df,
            ["amount_log"],
            ["Transaction_Type"],
            "Customer_ID",
        )


def test_modeling_rejects_missing_group_ids(modeling_df):
    modeling_df.loc[0, "Customer_ID"] = np.nan

    with pytest.raises(ValueError, match="missing values"):
        train_and_evaluate_oof(
            modeling_df,
            ["amount_log"],
            ["Transaction_Type"],
            "Customer_ID",
        )
