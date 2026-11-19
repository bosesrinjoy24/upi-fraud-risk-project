
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    brier_score_loss,
)
from sklearn.inspection import permutation_importance


def train_and_evaluate_oof(df, num_cols, cat_cols, group_col):
    if df.empty:
        raise ValueError("Input dataset cannot be empty.")

    if df["fraud"].nunique() != 2:
        raise ValueError("The fraud target must contain both binary classes.")

    if not df["fraud"].isin([0, 1]).all():
        raise ValueError("The fraud target must contain only 0 and 1.")

    if df[group_col].isna().any():
        raise ValueError(f"Grouping column '{group_col}' contains missing values.")

    feature_cols = num_cols + cat_cols

    if not feature_cols:
        raise ValueError("At least one feature is required.")

    missing_cols = [
        col for col in feature_cols + [group_col, "fraud"]
        if col not in df.columns
    ]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    X = df[feature_cols]
    y = df["fraud"]
    groups = df[group_col]

    sgkf = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                cat_cols,
            ),
        ]
    )

    models = {
        "Dummy": DummyClassifier(
            strategy="stratified",
            random_state=42,
        ),
        "LR": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        ),
        "RF": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=20,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }

    oof_preds = {
        name: np.full(len(df), np.nan)
        for name in models
    }

    fold_metrics = []
    pi_importances = []

    print(f"Running 5-Fold Stratified Group CV on {len(df)} rows...")

    for fold, (train_idx, test_idx) in enumerate(
        sgkf.split(X, y, groups)
    ):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        if y_train.nunique() != 2 or y_test.nunique() != 2:
            raise ValueError(
                f"Fold {fold + 1} does not contain both target classes."
            )

        for name, model in models.items():
            pipe = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("classifier", model),
                ]
            )

            pipe.fit(X_train, y_train)

            y_proba = pipe.predict_proba(X_test)[:, 1]
            y_pred = (y_proba >= 0.5).astype(int)

            oof_preds[name][test_idx] = y_proba

            tn, fp, fn, tp = confusion_matrix(
                y_test,
                y_pred,
                labels=[0, 1],
            ).ravel()

            fold_metrics.append({
                "Fold": fold + 1,
                "Model": name,
                "Train_Fraud_Rate": y_train.mean(),
                "Test_Fraud_Rate": y_test.mean(),
                "ROC_AUC": roc_auc_score(y_test, y_proba),
                "Avg_Prec": average_precision_score(y_test, y_proba),
                "Precision": precision_score(
                    y_test, y_pred, zero_division=0
                ),
                "Recall": recall_score(
                    y_test, y_pred, zero_division=0
                ),
                "F1": f1_score(
                    y_test, y_pred, zero_division=0
                ),
                "Brier_Score": brier_score_loss(y_test, y_proba),
                "TN": int(tn),
                "FP": int(fp),
                "FN": int(fn),
                "TP": int(tp),
                "Test_Rows": len(test_idx),
            })

            if name == "RF":
                result = permutation_importance(
                    pipe,
                    X_test,
                    y_test,
                    n_repeats=5,
                    random_state=42,
                    scoring="roc_auc",
                    n_jobs=1,
                )

                for i, col in enumerate(feature_cols):
                    pi_importances.append({
                        "Fold": fold + 1,
                        "Feature": col,
                        "Importance_Mean": result.importances_mean[i],
                        "Importance_Std": result.importances_std[i],
                    })

    for name, predictions in oof_preds.items():
        if np.isnan(predictions).any():
            raise RuntimeError(
                f"OOF predictions for {name} contain unfilled rows."
            )

    agg_rows = []

    for name, predictions in oof_preds.items():
        y_pred = (predictions >= 0.5).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y,
            y_pred,
            labels=[0, 1],
        ).ravel()

        agg_rows.append({
            "Model": name,
            "ROC_AUC": roc_auc_score(y, predictions),
            "Avg_Prec": average_precision_score(y, predictions),
            "Precision": precision_score(y, y_pred, zero_division=0),
            "Recall": recall_score(y, y_pred, zero_division=0),
            "F1": f1_score(y, y_pred, zero_division=0),
            "Brier_Score": brier_score_loss(y, predictions),
            "TN": int(tn),
            "FP": int(fp),
            "FN": int(fn),
            "TP": int(tp),
            "Total_Rows": len(y),
        })

    metrics_df = pd.DataFrame(fold_metrics)
    agg_metrics = pd.DataFrame(agg_rows)
    pi_df = pd.DataFrame(pi_importances)

    return (
        agg_metrics,
        metrics_df,
        oof_preds["RF"],
        y.reset_index(drop=True),
        pi_df,
    )
