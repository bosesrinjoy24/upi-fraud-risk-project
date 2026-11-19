
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


def simulate_costs_oof(
    y_true,
    y_proba_oof,
    thresholds,
    cost_investigation=20,
    cost_missed_fraud=500,
    scenario_name="Baseline",
):
    """
    Calculate financial and operational impact at different thresholds.
    """

    y_true = np.asarray(y_true)
    y_proba_oof = np.asarray(y_proba_oof, dtype=float)

    if y_true.ndim != 1 or y_proba_oof.ndim != 1:
        raise ValueError("Inputs must be one-dimensional.")

    if len(y_true) == 0:
        raise ValueError("Input dataset cannot be empty.")

    if len(y_true) != len(y_proba_oof):
        raise ValueError("y_true and y_proba_oof must have equal lengths.")

    if not np.isin(y_true, [0, 1]).all():
        raise ValueError("y_true must contain only binary labels 0 and 1.")

    if not np.isfinite(y_proba_oof).all():
        raise ValueError("Predicted probabilities must be finite.")

    if ((y_proba_oof < 0) | (y_proba_oof > 1)).any():
        raise ValueError("Predicted probabilities must be between 0 and 1.")

    try:
        thresholds = list(thresholds)
    except TypeError:
        raise ValueError("thresholds must be an iterable of numbers.")

    if not thresholds:
        raise ValueError("At least one threshold is required.")

    thresholds = np.asarray(thresholds, dtype=float)

    if not np.isfinite(thresholds).all():
        raise ValueError("Thresholds must be finite.")

    if ((thresholds < 0) | (thresholds > 1)).any():
        raise ValueError("Thresholds must be between 0 and 1.")

    for name, cost in [
        ("cost_investigation", cost_investigation),
        ("cost_missed_fraud", cost_missed_fraud),
    ]:
        if not np.isfinite(cost) or cost < 0:
            raise ValueError(f"{name} must be finite and non-negative.")

    if not isinstance(scenario_name, str) or not scenario_name.strip():
        raise ValueError("scenario_name must be a non-empty string.")

    results = []
    total_transactions = len(y_true)

    for threshold in thresholds:
        y_pred = (y_proba_oof >= threshold).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_true,
            y_pred,
            labels=[0, 1],
        ).ravel()

        flagged = tp + fp
        investigation_cost = flagged * cost_investigation
        missed_fraud_cost = fn * cost_missed_fraud
        total_cost = investigation_cost + missed_fraud_cost

        cost_per_txn = total_cost / total_transactions
        cost_per_detected = total_cost / tp if tp > 0 else np.nan
        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        workload_pct = flagged / total_transactions

        results.append({
            "Scenario": scenario_name,
            "Threshold": threshold,
            "Flagged": int(flagged),
            "TP": int(tp),
            "FP": int(fp),
            "FN": int(fn),
            "TN": int(tn),
            "Investigation_Cost": investigation_cost,
            "Missed_Fraud_Cost": missed_fraud_cost,
            "Total_Cost": total_cost,
            "Cost_Per_Txn": round(cost_per_txn, 2),
            "Cost_Per_Detected_Fraud": round(cost_per_detected, 2),
            "Detection_Rate": round(detection_rate, 4),
            "Investigation_Workload_Pct": round(workload_pct, 4),
        })

    return pd.DataFrame(results)
