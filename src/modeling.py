import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, confusion_matrix, brier_score_loss
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings('ignore')

def train_and_evaluate_oof(df, num_cols, cat_cols, group_col):
    X = df[num_cols + cat_cols]
    y = df['fraud']
    groups = df[group_col]
    
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
        ])

    models = {
        'Dummy': DummyClassifier(strategy='stratified', random_state=42),
        'LR': LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
        'RF': RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_leaf=20, class_weight='balanced', random_state=42, n_jobs=-1)
    }
    
    oof_preds = {name: np.zeros(len(df)) for name in models}
    fold_metrics = []
    pi_importances = []
    
    print(f"Running 5-Fold Stratified Group CV on {len(df)} rows...")
    for fold, (train_idx, test_idx) in enumerate(sgkf.split(X, y, groups)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        train_fraud_rate = y_train.mean()
        test_fraud_rate = y_test.mean()
        
        for name, model in models.items():
            pipe = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', model)])
            pipe.fit(X_train, y_train)
            
            y_proba = pipe.predict_proba(X_test)[:, 1]
            y_pred = (y_proba >= 0.5).astype(int)
            
            oof_preds[name][test_idx] = y_proba
            
            tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
            
            fold_metrics.append({
                'Fold': fold + 1, 'Model': name,
                'Train_Fraud_Rate': round(train_fraud_rate, 4),
                'Test_Fraud_Rate': round(test_fraud_rate, 4),
                'ROC_AUC': round(roc_auc_score(y_test, y_proba), 4),
                'Avg_Prec': round(average_precision_score(y_test, y_proba), 4),
                'Precision': round(precision_score(y_test, y_pred, zero_division=0), 4),
                'Recall': round(recall_score(y_test, y_pred, zero_division=0), 4),
                'F1': round(f1_score(y_test, y_pred, zero_division=0), 4),
                'Brier_Score': round(brier_score_loss(y_test, y_proba), 4),
                'TN': tn, 'FP': fp, 'FN': fn, 'TP': tp
            })
            
            # Permutation Importance for RF
            if name == 'RF':
                # Calculate on the test fold to ensure out-of-sample validity
                result = permutation_importance(pipe, X_test, y_test, n_repeats=5, random_state=42, scoring='roc_auc', n_jobs=-1)
                for i, col in enumerate(X.columns):
                    pi_importances.append({
                        'Fold': fold + 1,
                        'Feature': col,
                        'Importance_Mean': result.importances_mean[i],
                        'Importance_Std': result.importances_std[i]
                    })

    metrics_df = pd.DataFrame(fold_metrics)
    agg_metrics = metrics_df.groupby('Model').mean(numeric_only=True).reset_index()
    pi_df = pd.DataFrame(pi_importances)
    
    return agg_metrics, metrics_df, oof_preds['RF'], y, pi_df