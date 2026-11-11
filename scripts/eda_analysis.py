import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_data, ROOT_DIR
from src.features import engineer_features
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, chi2_contingency

def cramers_v(x, y):
    """Calculate Cramér's V for categorical association."""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    # Bias correction
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))

def rank_biserial(u_stat, n1, n2):
    """Calculate Rank-Biserial Correlation for Mann-Whitney U."""
    return 1 - (2 * u_stat) / (n1 * n2)

def main():
    print("Loading data...")
    df = load_data()
    df = engineer_features(df)
    
    out_dir = ROOT_DIR / "outputs"
    out_dir.mkdir(exist_ok=True)

    # 1. Overall Distribution
    summary_data = {
        'Metric': ['Total Transactions', 'Fraud Count', 'Genuine Count', 'Fraud Rate', 'Mean Amount (Fraud)', 'Mean Amount (Genuine)'],
        'Value': [
            len(df), 
            df['fraud'].sum(), 
            len(df) - df['fraud'].sum(), 
            round(df['fraud'].mean(), 4),
            round(df[df['fraud']==1]['amount'].mean(), 2),
            round(df[df['fraud']==0]['amount'].mean(), 2)
        ]
    }
    pd.DataFrame(summary_data).to_csv(out_dir / 'eda_summary.csv', index=False)

    # 2. Statistical Tests: Continuous Variables (Mann-Whitney U)
    continuous_vars = ['amount', 'Transaction_Frequency', 'Days_Since_Last_Transaction']
    stat_results = []
    
    for var in continuous_vars:
        fraud_vals = df[df['fraud'] == 1][var]
        genuine_vals = df[df['fraud'] == 0][var]
        
        stat, p_value = mannwhitneyu(fraud_vals, genuine_vals, alternative='two-sided')
        effect_size = rank_biserial(stat, len(fraud_vals), len(genuine_vals))
        
        stat_results.append({
            'Variable': var,
            'Test': 'Mann-Whitney U',
            'P_Value': p_value,
            'Effect_Size': round(abs(effect_size), 4),
            'Interpretation': 'Negligible' if abs(effect_size) < 0.1 else ('Small' if abs(effect_size) < 0.3 else 'Moderate/Strong')
        })

    # 3. Statistical Tests: Categorical Variables (Chi-Square)
    categorical_vars = ['Transaction_Type', 'Payment_Gateway', 'Merchant_Category', 'Transaction_Channel', 'Device_OS']
    
    for var in categorical_vars:
        contingency_table = pd.crosstab(df[var], df['fraud'])
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        effect_size = cramers_v(df[var], df['fraud'])
        
        stat_results.append({
            'Variable': var,
            'Test': 'Chi-Square',
            'P_Value': p_value,
            'Effect_Size': round(effect_size, 4),
            'Interpretation': 'Negligible' if effect_size < 0.1 else ('Small' if effect_size < 0.3 else 'Moderate/Strong')
        })

    # Save results
    results_df = pd.DataFrame(stat_results)
    # Format P-values to scientific notation for readability
    results_df['P_Value'] = results_df['P_Value'].apply(lambda x: f"{x:.4e}")
    
    results_df.to_csv(out_dir / 'statistical_tests.csv', index=False)
    
    print("\n--- Statistical Test Results ---")
    print(results_df.to_string(index=False))
    print("\nNote: Due to N=100,000, p-values may be significant, but effect sizes < 0.1 indicate no practical business importance.")
    print(f"\nSaved outputs to {out_dir}")

if __name__ == "__main__":
    main()