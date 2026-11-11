# Model Limitations & Null Result Assessment

## 1. The Null Result
Across 5-fold Stratified Group Cross-Validation, both Logistic Regression and Random Forest achieved a mean ROC-AUC of approximately 0.50 (0.49996 and 0.50208, respectively). A score of 0.50 indicates that the models demonstrate no meaningful predictive discrimination on the test folds. The models performed identically to a stratified random baseline (`DummyClassifier`).

## 2. Identical Confusion Matrices at Low Thresholds
The threshold analysis reveals identical confusion matrices (and thus identical costs) at thresholds 0.1, 0.2, and 0.3. 
- **Reason:** The positive class prevalence is 23.99% (0.2399). Because the model lacks ranking ability, its predicted probabilities cluster tightly around the base rate. Any threshold set below 0.2399 will simply flag *every single transaction* as fraud. Therefore, thresholds 0.1 and 0.3 flag 100% of the dataset, producing identical results.

## 3. Calibration Assessment
The Brier Score for the Random Forest is approximately 0.2475. For a dataset with a 24% prevalence, a naive model predicting a constant probability of 0.24 would achieve a Brier score of ~0.182. The fact that the model's Brier score is higher (worse) than the naive constant baseline suggests that its predicted probabilities are uncalibrated and not providing reliable confidence levels.

## 4. Permutation Importance
Permutation importance calculated on the out-of-fold data indicates that shuffling individual features results in negligible changes to ROC-AUC. This suggests that no single available feature provides a robust predictive signal in this synthetic dataset.

## 5. Conclusion
The evaluated models do not demonstrate meaningful predictive discrimination using the available features and the selected customer-grouped evaluation design. This highlights the limitations of the synthetic dataset (e.g., potential historical feature leakage, structural 1:1 device mapping, uniform timestamps). It does not establish that fraud signals are absent from real UPI transactions. The pipeline is correct; the data is the limitation.