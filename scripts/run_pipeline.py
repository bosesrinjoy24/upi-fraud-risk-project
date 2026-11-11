import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_data, ROOT_DIR
from src.validation import validate_transactions
from src.features import engineer_features, get_feature_columns
from src.modeling import train_and_evaluate_oof
from src.cost_simulator import simulate_costs_oof
import pandas as pd

def main():
    print("Loading data...")
    df = load_data()
    validate_transactions(df) 

    print("\nEngineering features...")
    df = engineer_features(df)
    num_cols, cat_cols = get_feature_columns()

    print("\nTraining models (Out-of-Fold Cross-Validation)...")
    agg_metrics, fold_metrics, oof_proba_rf, y_true, pi_df = train_and_evaluate_oof(df, num_cols, cat_cols, 'Customer_ID')

    print("\n--- Aggregated Cross-Validation Metrics ---")
    print(agg_metrics[['Model', 'ROC_AUC', 'Avg_Prec', 'Precision', 'Recall', 'F1', 'Brier_Score']].to_string(index=False))

    print("\n--- Business Cost Simulation & Sensitivity Analysis ---")
    thresholds = [0.1, 0.3, 0.5, 0.7]
    
    # Scenario 1: Baseline (Cheap investigation, Moderate fraud loss)
    df_base = simulate_costs_oof(y_true, oof_proba_rf, thresholds, cost_investigation=20, cost_missed_fraud=500, scenario_name="Baseline")
    
    # Scenario 2: High Investigation Cost (e.g., manual review requires senior analyst)
    df_high_inv = simulate_costs_oof(y_true, oof_proba_rf, thresholds, cost_investigation=100, cost_missed_fraud=500, scenario_name="High Investigation Cost")
    
    # Scenario 3: High Missed Fraud Cost (e.g., high-value B2B transactions)
    df_high_fraud = simulate_costs_oof(y_true, oof_proba_rf, thresholds, cost_investigation=20, cost_missed_fraud=2000, scenario_name="High Fraud Loss")

    # Combine all scenarios
    all_scenarios = pd.concat([df_base, df_high_inv, df_high_fraud], ignore_index=True)
    
    print("\nBaseline Scenario Costs:")
    print(df_base[['Threshold', 'Total_Cost', 'Cost_Per_Txn', 'Investigation_Workload_Pct', 'Detection_Rate']].to_string(index=False))
    
    out_dir = ROOT_DIR / "outputs"
    out_dir.mkdir(exist_ok=True)
    
    # Save outputs
    all_scenarios.to_csv(out_dir / 'cost_simulation.csv', index=False)
    agg_metrics.to_csv(out_dir / 'model_metrics.csv', index=False)
    fold_metrics.to_csv(out_dir / 'fold_metrics.csv', index=False)
    pd.DataFrame({'y_true': y_true, 'y_proba_rf': oof_proba_rf}).to_csv(out_dir / 'oof_predictions.csv', index=False)
    pi_df.to_csv(out_dir / 'permutation_importance.csv', index=False)
    
    print(f"\nSaved all outputs to {out_dir}")

if __name__ == "__main__":
    main()