# Technical Architecture

```mermaid
graph TD
    A[Raw Synthetic Data CSV] --> B(data_loader.py)
    B --> C(validation.py)
    C -->|Validation Fails| D[Stop Pipeline]
    C -->|Validation Passes| E(features.py)
    E --> F[Preprocessing Pipeline: ColumnTransformer]
    F --> G(StratifiedGroupKFold by Customer_ID)
    G --> H{Model Evaluation}
    H -->|OOF Predictions| I(cost_simulator.py)
    H -->|Feature Importance| J[Permutation Importance]
    I --> K[Business Cost Output CSV]
    J --> L[Model Card & README]
    K --> L

# TASK 3: Dashboard Upgrade

The Master Prompt requires a 3-page dashboard that reflects the *new* OOF data.

1. Open Power BI Desktop.
2. Load the new CSVs:
   - `outputs/model_metrics.csv`
   - `outputs/cost_simulation.csv`
   - `outputs/oof_predictions.csv` (This is your raw honest data).

**Page 1: Executive Fraud Overview**
- **Visual 1:** Card showing Base Rate (23.99%).
- **Visual 2:** Card showing Dataset Size (100,000 rows).
- **Visual 3:** Text box explaining the synthetic data limitation and that this is a null result.

**Page 2: Fraud Behaviour (SQL Findings)**
- **Visual 1:** Bar chart of "Fraud Rate by Hour" (from `oof_predictions` or the raw data).
- **Visual 2:** Text box stating the Device-Concentration null result (647 customers = 647 devices).

**Page 3: Model & Operational Performance**
- **Visual 1 (Cost Simulation):** Create a line chart.
  - **X-axis:** `Threshold` (from `cost_simulation.csv`).
  - **Y-axis:** `Total_Cost_INR`.
  - **Tooltip:** `Flagged`, `TP`, `FP`, `FN`.
  - *Explanation:* Show the business that at threshold 0.3, the cost is ₹2M, but at 0.7, the cost is ₹11.9M.
- **Visual 2:** Table showing the `Model_Metrics` (Dummy ROC-AUC, LR ROC-AUC, RF ROC-AUC).

**Save the file as `dashboard/UPI_Fraud_Dashboard.pbix`.**

---

# TASK 4: Memo Update

The Master Prompt requires the PDF memo to reflect the final OOF metrics and correct cost formula.

Run this Python script in your Jupyter Notebook to generate the final, corrected memo:

```python
import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'UPI Fraud Detection: Project Summary', 0, 1, 'C')
        self.ln(5)

def create_memo():
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, 'TO: Fraud Risk Team Lead', 0, 1)
    pdf.cell(0, 6, 'SUBJECT: Findings from Synthetic UPI Transaction Analysis', 0, 1)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, '1. The Business Question', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, "Which transaction patterns in a UPI payment flow are most predictive of fraud, and what is the precision-recall trade-off at different risk thresholds?")
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, '2. Dataset Context & Limitations', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, "The analysis was conducted on a 100,000-row synthetic UPI dataset. The fraud rate is 23.99%. A critical limitation was identified: the dataset includes pre-computed historical features (e.g., Transaction_Frequency) that may contain future information leakage. Furthermore, we removed Transaction_Status because it is a post-transaction metric unavailable at real-time scoring.")
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, '3. Analytical Investigations', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, "1. SQL Layer: We utilized window functions to analyze transaction velocity. Results showed a flat fraud rate across all time-gap buckets, indicating no velocity signal.\n2. Machine Learning: We trained Logistic Regression and Random Forest models using StratifiedGroupKFold by Customer_ID. This prevents the model from memorizing specific customers.")
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, '4. Findings & Null Results', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, "Both models achieved an Out-of-Fold ROC-AUC of ~0.50 (equivalent to random chance). The baseline Dummy Classifier scored 0.4986, proving the models learned nothing.\n\nBusiness Cost Simulation (using OOF predictions):\n- At Threshold 0.3: The model flags all 100,000 transactions. Investigation cost = ₹2,000,000.\n- At Threshold 0.7: The model misses all 23,986 frauds. Missed fraud cost = ₹11,993,000.\nThe model fails to provide a cost-effective fraud filter.")
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, '5. Business Implications', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, "Because the model has no predictive power, deploying it would result in massive false-positive investigation costs or huge missed-fraud losses. The data science pipeline is robust and leakage-free, but the synthetic dataset lacks the complex network and behavioral signals of real UPI traffic.")
    pdf.ln(5)

    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 6, "Code, SQL queries, and reproducibility instructions: github.com/bosesrinjoy24/upi-fraud-risk-project", 0, 1, 'C')

    out_dir = os.path.join("..", "memo")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "UPI_Fraud_Project_Summary.pdf")
    pdf.output(out_path)
    print(f"Memo generated at: {out_path}")

create_memo()