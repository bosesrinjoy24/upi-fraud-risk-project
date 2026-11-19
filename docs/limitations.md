# Model Limitations and Null Result Assessment

## 1. Main Finding

The five-fold customer-grouped out-of-fold evaluation produced the following ROC-AUC scores:

| Model | ROC-AUC |
|---|---:|
| Dummy Classifier | 0.498613 |
| Logistic Regression | 0.500590 |
| Random Forest | 0.501776 |

Both trained models are close to chance-level discrimination. The evaluated feature set did not demonstrate meaningful fraud-ranking performance under this evaluation design.

## 2. What This Does Not Prove

This result does not establish that the dataset contains absolutely no learnable fraud signals.

Possible explanations include:

- The excluded historical features may contain useful information, but their provenance could not be verified.
- The selected features may not capture network and behavioural interactions associated with fraud.
- The synthetic data-generation process may not encode useful patterns in the available predictors.
- Different verified features or modelling approaches may produce different results.

The conclusion applies to the tested dataset, feature set, models, and validation design.

## 3. Probability Quality

The Random Forest Brier score was approximately 0.247696.

A constant prediction equal to the dataset fraud prevalence of 0.23986 would have a Brier score of approximately 0.182327 on this dataset.

The Random Forest therefore has worse overall squared probability error than this prevalence-only reference.

The mean Random Forest out-of-fold predicted probability is 0.495102, compared with the observed fraud prevalence of 0.239860. The predicted probabilities range from 0.416947 to 0.572974.

This substantial difference from the observed prevalence, together with the worse Brier score, indicates poor probability quality. A reliability diagram or dedicated calibration analysis would be needed to characterize calibration more fully.

A Brier score combines calibration and predictive resolution. This comparison alone does not isolate calibration.

## 4. Threshold Behaviour

The out-of-fold Random Forest probabilities range from 0.416947 to 0.572974, with a mean of 0.495102. Consequently, every prediction exceeds thresholds 0.1 and 0.3, while no prediction reaches 0.7.

Observed baseline cost-simulation results:

| Threshold | Investigation workload | Detection rate | Total cost |
|---:|---:|---:|---:|
| 0.1 | 100.00% | 100.00% | ₹2,000,000 |
| 0.3 | 100.00% | 100.00% | ₹2,000,000 |
| 0.5 | 37.71% | 37.86% | ₹8,206,660 |
| 0.7 | 0.00% | 0.00% | ₹11,993,000 |

The cost simulation assumes ₹20 per investigation and ₹500 per missed fraudulent transaction. These are illustrative assumptions, not observed financial losses.

Thresholds 0.1 and 0.3 flag every transaction. A threshold of 0.7 flags none. These results do not establish a useful operational threshold.

## 5. Synthetic Data Limitation

The dataset contains 100,000 transactions and 23,986 fraud-labelled rows, corresponding to a 23.986% fraud share.

This is the observed class distribution in this dataset, not an estimate of the real-world UPI fraud rate.

## 6. Overall Assessment

The project demonstrates a reproducible analytical workflow and an honest null-result evaluation. It does not establish a deployable fraud detection system or production readiness.
