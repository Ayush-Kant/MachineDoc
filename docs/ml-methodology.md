# FleetGuard ML Methodology (To Be Validated)

This document is an experiment plan. No algorithm is selected as a winner and no performance result is claimed yet.

## 1. Prediction task

For each engine at an observed cycle, estimate the number of additional operating cycles until the simulated failure endpoint. The official training trajectories run to failure; test trajectories are truncated and accompanied by one final RUL label per engine.

## 2. Target alternatives

Evaluate:
- Uncapped RUL target derived from the complete training trajectory.
- A capped target (for example, a cap selected after literature and data exploration) to reduce emphasis on early-life cycles where degradation may be weak.

The cap is a hyperparameter/design decision, not a property to assume about the raw files. Report which target formulation was used.

## 3. Validation design

Candidate protocol:
- Split training engine IDs into train and validation groups.
- Keep every time row for an engine within one group.
- Fit preprocessing only on the training-engine subset.
- Tune hyperparameters on validation engines.
- Keep the official test set sealed for final benchmark evaluation.
- Evaluate the final observed row of every test engine against its supplied RUL label.

Document random seed, unit IDs per split, feature list and all preprocessing parameters.

## 4. Baselines and candidate models

Start with simple baselines:
- Predict a constant based on training target statistics.
- Linear regression or a tree-based regressor.

Then compare a small set of suitable candidates:
- RandomForestRegressor.
- Gradient boosting regressor (scikit-learn HistGradientBoostingRegressor or another justified implementation).
- Optional XGBoost only if installation, licence and reproducibility are acceptable.

Use scikit-learn IsolationForest as one anomaly-detection candidate, alongside a transparent statistical baseline. Anomaly labels are not directly supplied as a per-row classification target, so anomaly evaluation must be described carefully and should not claim supervised accuracy without valid labels.

## 5. Metrics

For RUL regression:
- MAE.
- RMSE.
- NASA asymmetric scoring function as defined by the benchmark convention.
- Per-engine prediction error distribution and residual plots.

For anomaly detection:
- Detection rate on explicitly injected synthetic corruptions, if used.
- False-positive rate on unmodified validation data.
- Qualitative review of temporal anomalies.
- Threshold selection based on validation data only.

Keep benchmark RUL error and anomaly detection evaluation separate.

## 6. Feature engineering candidates

- Raw sensor values.
- Rolling mean and standard deviation within engine.
- Rolling trend / slope.
- Difference from previous cycle.
- Operating settings.
- Selected lag features.

Rolling/lag features must be computed after sorting by engine and cycle and must never cross engine boundaries.

## 7. Inference contract

Input: a validated observation or engine history with schema version and ordered cycles.

Output:
- engine ID and latest cycle
- predicted RUL in cycles
- anomaly score / flag (separate from RUL)
- model version
- feature schema version
- prediction timestamp
- data-quality status
- optional confidence or uncertainty only if calibrated and validated

## 8. Promotion criteria

A candidate is not promoted merely because it trained successfully. Require:
- validation metrics and final test protocol recorded,
- no leakage checks failing,
- artifact and preprocessing reproducibility,
- inference contract compatibility,
- documented comparison with current approved model,
- explicit approval step.
