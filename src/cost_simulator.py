import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix

def simulate_costs_oof(y_true, y_proba_oof, thresholds, cost_investigation=20, cost_missed_fraud=500, scenario_name="Baseline"):
    """
    Calculates the financial and operational impact of fraud at different thresholds.
    """
    results = []
    total_transactions = len(y_true)
    
    for t in thresholds:
        y_pred = (y_proba_oof >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        flagged = tp + fp
        inv_cost = flagged * cost_investigation
        missed_cost = fn * cost_missed_fraud
        total_cost = inv_cost + missed_cost
        
        # Operational Metrics
        cost_per_txn = total_cost / total_transactions
        # Prevent division by zero if tp is 0
        cost_per_detected = total_cost / tp if tp > 0 else 0
        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        workload_pct = flagged / total_transactions
        
        results.append({
            'Scenario': scenario_name,
            'Threshold': t,
            'Flagged': int(flagged),
            'TP': int(tp),
            'FP': int(fp),
            'FN': int(fn),
            'TN': int(tn),
            'Investigation_Cost': inv_cost,
            'Missed_Fraud_Cost': missed_cost,
            'Total_Cost': total_cost,
            'Cost_Per_Txn': round(cost_per_txn, 2),
            'Cost_Per_Detected_Fraud': round(cost_per_detected, 2),
            'Detection_Rate': round(detection_rate, 4),
            'Investigation_Workload_Pct': round(workload_pct, 4)
        })
        
    return pd.DataFrame(results)