from pathlib import Path
import csv
from fpdf import FPDF


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "memo" / "UPI_Fraud_Project_Summary.pdf"
OUTPUTS = ROOT / "outputs"


def read_csv(name):
    path = OUTPUTS / name
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


eda = read_csv("eda_summary.csv")
models = read_csv("model_metrics.csv")
folds = read_csv("fold_metrics.csv")
costs = read_csv("cost_simulation.csv")
tests = read_csv("statistical_tests.csv")
importance = read_csv("permutation_importance.csv")


if len(models) != 3 or len(folds) != 15 or len(costs) != 12:
    raise ValueError("Unexpected report input dimensions. PDF not generated.")


def metric(name):
    for row in eda:
        if row["Metric"] == name:
            return float(row["Value"])
    raise KeyError(name)


def model(name):
    for row in models:
        if row["Model"] == name:
            return row
    raise KeyError(name)


def cost(scenario, threshold):
    for row in costs:
        if row["Scenario"] == scenario and float(row["Threshold"]) == threshold:
            return row
    raise KeyError((scenario, threshold))


rf = model("RF")
lr = model("LR")
baseline_05 = cost("Baseline", 0.5)
baseline_01 = cost("Baseline", 0.1)
baseline_07 = cost("Baseline", 0.7)


class MemoPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.cell(0, 8, f"UPI Fraud Risk Analytics | Page {self.page_no()}", align="C")


pdf = MemoPDF()
pdf.set_auto_page_break(auto=True, margin=16)
pdf.set_margins(14, 14, 14)
pdf.set_title("UPI Fraud Risk Analytics - Project Summary")
pdf.set_author("UPI Fraud Risk Analytics Project")


def heading(text, level=1):
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 15 if level == 1 else 11)
    pdf.multi_cell(pdf.epw, 8 if level == 1 else 6, text)
    pdf.ln(1)


def paragraph(text):
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(pdf.epw, 5, text)
    pdf.ln(2)


def bullet(text):
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(pdf.epw, 5, "- " + text)
    pdf.ln(1)


def table(headers, rows, widths, font_size=8):
    pdf.set_font("Helvetica", "B", font_size)
    for header, width in zip(headers, widths):
        pdf.cell(width, 8, str(header), border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", size=font_size)
    for row in rows:
        for value, width in zip(row, widths):
            pdf.cell(width, 7, str(value), border=1, align="C")
        pdf.ln()
    pdf.ln(3)


def fmt(value, digits=3):
    return f"{float(value):.{digits}f}"


# PAGE 1
pdf.add_page()
pdf.set_font("Helvetica", "B", 21)
pdf.multi_cell(pdf.epw, 11, "UPI FRAUD RISK ANALYTICS")
pdf.set_font("Helvetica", size=12)
pdf.multi_cell(pdf.epw, 8, "Project Summary and Evaluation Memo")
pdf.ln(4)

heading("Executive Summary")
paragraph(
    "This project implements an end-to-end transaction fraud analytics workflow "
    "using a 100,000-row synthetic UPI transaction dataset. It covers data "
    "validation, exploratory analysis, SQL investigations, leakage-conscious "
    "feature preparation, grouped cross-validation, model evaluation and "
    "illustrative cost simulation."
)
paragraph(
    "The evaluated models did not demonstrate meaningful fraud-ranking "
    "performance. Random Forest achieved a pooled out-of-fold ROC-AUC of "
    f"{fmt(rf['ROC_AUC'], 4)}, while Logistic Regression achieved "
    f"{fmt(lr['ROC_AUC'], 4)}. These values are close to random ranking. "
    "The models are not suitable for production fraud decisions."
)

heading("Dataset Profile")
table(
    ["Measure", "Value"],
    [
        ["Transactions", f"{int(metric('Total Transactions')):,}"],
        ["Fraud-labelled", f"{int(metric('Fraud Count')):,}"],
        ["Genuine-labelled", f"{int(metric('Genuine Count')):,}"],
        ["Fraud-labelled rate", f"{metric('Fraud Rate') * 100:.2f}%"],
        ["Mean amount - fraud", f"{metric('Mean Amount (Fraud)'):.2f}"],
        ["Mean amount - genuine", f"{metric('Mean Amount (Genuine)'):.2f}"],
    ],
    [95, 85],
)
paragraph(
    "The dataset is synthetic. Its fraud-label prevalence is a property of "
    "this dataset and must not be interpreted as the real-world UPI fraud rate."
)

heading("Project Scope")
bullet("Validate and inspect the transaction dataset.")
bullet("Explore transaction, device, customer and time-gap patterns.")
bullet("Run SQL-based descriptive investigations.")
bullet("Train Dummy, Logistic Regression and Random Forest baselines.")
bullet("Evaluate using five-fold StratifiedGroupKFold grouped by Customer_ID.")
bullet("Generate out-of-fold predictions and illustrative threshold cost scenarios.")

# PAGE 2
pdf.add_page()
heading("Methodology and Controls")
paragraph(
    "The modelling workflow uses preprocessing pipelines so transformations "
    "are fitted within each training fold. Validation uses five-fold "
    "StratifiedGroupKFold with Customer_ID as the grouping variable, "
    "separating customers between training and test folds."
)
paragraph(
    "Out-of-fold predictions are used for pooled evaluation and cost "
    "simulation. This avoids calculating business costs from predictions "
    "made on the same observations used to fit each model."
)
paragraph(
    "The selected feature set contains four numeric features "
    "(amount_log, hour, day_of_week and is_weekend) and five categorical "
    "features (Transaction_Type, Payment_Gateway, Merchant_Category, "
    "Transaction_Channel and Device_OS)."
)
paragraph(
    "Transaction_Status was excluded as a post-transaction field. "
    "Transaction_Frequency, Transaction_Amount_Deviation and "
    "Days_Since_Last_Transaction were excluded because their provenance "
    "and point-in-time availability could not be verified."
)

heading("Model Performance")
table(
    ["Model", "ROC-AUC", "Avg Prec.", "Precision", "Recall", "F1", "Brier"],
    [
        [
            row["Model"],
            fmt(row["ROC_AUC"]),
            fmt(row["Avg_Prec"]),
            fmt(row["Precision"]),
            fmt(row["Recall"]),
            fmt(row["F1"]),
            fmt(row["Brier_Score"]),
        ]
        for row in models
    ],
    [22, 27, 27, 27, 27, 25, 25],
    7,
)
paragraph(
    "ROC-AUC and average precision are ranking metrics. Precision, recall "
    "and F1 are threshold-dependent metrics reported at the configured "
    "classification threshold of 0.5. Brier score measures probability "
    "prediction error; lower is better. The RF Brier score is approximately "
    f"{fmt(rf['Brier_Score'], 4)}."
)
paragraph(
    "The pooled out-of-fold results show no meaningful discrimination. "
    "The threshold-dependent recall and precision do not change that "
    "conclusion: a model can flag many transactions without ranking fraud "
    "effectively."
)

heading("Cross-validation")
paragraph(
    f"The fold-level evaluation contains {len(folds)} model-fold records "
    f"({len(folds) // 3} folds across three model types). Fold-level results "
    "are retained in outputs/fold_metrics.csv for detailed inspection."
)

# PAGE 3
pdf.add_page()
heading("Exploratory and Statistical Findings")
paragraph(
    "The exploratory analysis found similar average transaction amounts "
    "for fraud-labelled and genuine-labelled records. The mean amounts "
    f"were {metric('Mean Amount (Fraud)'):.2f} and "
    f"{metric('Mean Amount (Genuine)'):.2f}, respectively."
)

table(
    ["Variable", "Test", "P-value", "Effect size", "Interpretation"],
    [
        [
            row["Variable"],
            row["Test"],
            fmt(row["P_Value"], 4),
            fmt(row["Effect_Size"], 4),
            row["Interpretation"],
        ]
        for row in tests
    ],
    [34, 37, 29, 32, 45],
    6,
)
paragraph(
    "Transaction_Type has a p-value below 0.05, but its effect size is "
    "negligible. Statistical significance alone does not establish useful "
    "predictive value. The other tested variables also show negligible "
    "effect sizes in this analysis."
)

heading("SQL Investigation Findings")
bullet(
    "Time-gap velocity buckets show broadly similar fraud rates; no strong "
    "velocity signal was established by this descriptive analysis."
)
bullet(
    "The top device and customer summaries show one-to-one mappings in "
    "the inspected top records. This is not proof that device sharing "
    "never occurs."
)
bullet(
    "The dataset contains 99,998 unique IP addresses across 100,000 rows; "
    "two IP addresses are duplicated. Shared IPs are investigation signals, "
    "not proof of fraud."
)
paragraph(
    "The SQL velocity analysis covers 99,353 rows because the first "
    "transaction for each customer has no prior transaction time-gap."
)

heading("Permutation Importance")
paragraph(
    f"The permutation importance output contains {len(importance)} "
    "fold-feature records. Importance values are diagnostic and should "
    "not be interpreted as evidence of causal relationships. Near-zero "
    "or negative values are consistent with the weak predictive signal "
    "observed in the model evaluation."
)

# PAGE 4
pdf.add_page()
heading("Illustrative Business Cost Simulation")
paragraph(
    "The cost simulator evaluates out-of-fold Random Forest probabilities "
    "under multiple thresholds and cost scenarios. The cost assumptions "
    "are hypothetical project inputs, not measured bank investigation "
    "costs or observed customer losses."
)

table(
    ["Threshold", "Flagged", "TP", "FP", "FN", "Total cost (INR)"],
    [
        [
            f"{float(row['Threshold']):.1f}",
            f"{int(row['Flagged']):,}",
            f"{int(row['TP']):,}",
            f"{int(row['FP']):,}",
            f"{int(row['FN']):,}",
            f"{float(row['Total_Cost']):,.0f}",
        ]
        for row in costs if row["Scenario"] == "Baseline"
    ],
    [27, 30, 25, 30, 25, 42],
    7,
)

paragraph(
    f"At threshold 0.5, {int(baseline_05['Flagged']):,} transactions are "
    f"flagged, including {int(baseline_05['TP']):,} fraud-labelled and "
    f"{int(baseline_05['FP']):,} genuine-labelled transactions. "
    f"{int(baseline_05['FN']):,} fraud-labelled transactions are missed. "
    f"The simulated total cost is INR {float(baseline_05['Total_Cost']):,.0f}."
)
paragraph(
    f"At threshold 0.1, all {int(baseline_01['Flagged']):,} transactions "
    "are flagged. At threshold 0.7, no transactions are flagged and all "
    f"{int(baseline_07['FN']):,} fraud-labelled records are missed. "
    "These extreme outcomes illustrate the limitations of the model's "
    "out-of-fold score distribution."
)
paragraph(
    "The baseline cost outputs are consistent with an illustrative "
    "investigation cost of INR 20 per flagged transaction and a missed-fraud "
    "cost of INR 500 per missed fraud-labelled transaction. These are "
    "simulation assumptions, not empirical estimates."
)

heading("Limitations and Responsible Use")
bullet("The dataset is synthetic and has an unusually high fraud-label prevalence.")
bullet("The evaluated models have ROC-AUC close to 0.50.")
bullet("The selected features may not contain the signals needed to distinguish fraud.")
bullet("Historical feature provenance and point-in-time validity were not established.")
bullet("Cost outputs depend entirely on hypothetical cost assumptions.")
bullet("Descriptive associations do not establish causation or operational fraud rules.")
bullet("No production deployment, live transaction testing or real-world validation was performed.")

heading("Conclusion and Next Steps")
paragraph(
    "The project demonstrates a reproducible analytics workflow and "
    "documents important validation and leakage controls. Its central "
    "result is negative: the current synthetic dataset and selected "
    "features do not support a useful fraud classifier."
)
paragraph(
    "Further modelling should be considered only after obtaining "
    "representative, appropriately governed transaction data with "
    "verified labels, realistic prevalence, point-in-time features and "
    "a documented operational cost framework. Any future model would "
    "require independent validation, calibration assessment, monitoring "
    "and controlled operational testing before deployment."
)

heading("Reproducibility References")
for item in [
    "outputs/model_metrics.csv",
    "outputs/fold_metrics.csv",
    "outputs/oof_predictions.csv",
    "outputs/cost_simulation.csv",
    "outputs/eda_summary.csv",
    "outputs/statistical_tests.csv",
    "outputs/permutation_importance.csv",
    "docs/model_card.md",
    "docs/limitations.md",
    "docs/feature_provenance.md",
    "docs/methodology_decision_log.md",
]:
    bullet(item)

OUT.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(OUT))

if not OUT.exists() or OUT.stat().st_size < 3000:
    raise RuntimeError("Generated PDF failed basic size validation.")

print("[PASS] Revised project memo generated.")
print("PATH:", OUT)
print("SIZE:", OUT.stat().st_size, "bytes")
print("PAGES:", pdf.page_no())
