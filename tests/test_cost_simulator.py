import numpy as np
import pytest

from src.cost_simulator import simulate_costs_oof


def test_cost_simulation_calculates_expected_values():
    result = simulate_costs_oof(
        y_true=[0, 0, 1, 1],
        y_proba_oof=[0.1, 0.8, 0.9, 0.2],
        thresholds=[0.5],
        cost_investigation=20,
        cost_missed_fraud=500,
    )

    row = result.iloc[0]

    assert row["TP"] == 1
    assert row["FP"] == 1
    assert row["FN"] == 1
    assert row["TN"] == 1
    assert row["Flagged"] == 2
    assert row["Investigation_Cost"] == 40
    assert row["Missed_Fraud_Cost"] == 500
    assert row["Total_Cost"] == 540
    assert row["Cost_Per_Txn"] == 135
    assert row["Cost_Per_Detected_Fraud"] == 540
    assert row["Detection_Rate"] == 0.5
    assert row["Investigation_Workload_Pct"] == 0.5


def test_cost_simulation_handles_missing_predicted_class():
    result = simulate_costs_oof(
        y_true=[0, 0, 1, 1],
        y_proba_oof=[0.1, 0.2, 0.3, 0.4],
        thresholds=[0.9],
    )

    row = result.iloc[0]

    assert row["TP"] == 0
    assert row["FP"] == 0
    assert row["FN"] == 2
    assert row["TN"] == 2
    assert np.isnan(row["Cost_Per_Detected_Fraud"])


@pytest.mark.parametrize(
    "y_true, probabilities, thresholds",
    [
        ([], [], [0.5]),
        ([0, 1], [0.2], [0.5]),
        ([0, 2], [0.2, 0.8], [0.5]),
        ([0, 1], [0.2, np.nan], [0.5]),
        ([0, 1], [0.2, 1.2], [0.5]),
        ([0, 1], [0.2, 0.8], []),
        ([0, 1], [0.2, 0.8], [-0.1]),
        ([0, 1], [0.2, 0.8], [1.1]),
    ],
)
def test_cost_simulation_rejects_invalid_inputs(
    y_true, probabilities, thresholds
):
    with pytest.raises(ValueError):
        simulate_costs_oof(y_true, probabilities, thresholds)


@pytest.mark.parametrize(
    "investigation_cost, missed_fraud_cost",
    [
        (-1, 500),
        (20, -1),
        (np.inf, 500),
    ],
)
def test_cost_simulation_rejects_invalid_costs(
    investigation_cost, missed_fraud_cost
):
    with pytest.raises(ValueError):
        simulate_costs_oof(
            [0, 1],
            [0.2, 0.8],
            [0.5],
            cost_investigation=investigation_cost,
            cost_missed_fraud=missed_fraud_cost,
        )
