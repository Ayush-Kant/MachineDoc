# FleetGuard System Architecture (Initial Proposal)

## 1. Architectural boundary

The first version is a local, software-only application. The benchmark pipeline consumes NASA C-MAPSS files. A deterministic simulator may replay or stream rows from these files to demonstrate operational monitoring. It must label these events as simulated telemetry.

## 2. Logical components

### Data and ML plane

1. **Dataset adapter:** reads original C-MAPSS train, test and RUL files.
2. **Validation layer:** schema, type, range, missingness, uniqueness, cycle-order and RUL alignment checks.
3. **Feature pipeline:** per-engine temporal features, operating settings and sensor transformations.
4. **Model training:** separate anomaly-detection and RUL-regression experiments.
5. **Evaluation:** engine-level validation, metrics, residual analysis and benchmark endpoint predictions.
6. **Model registry:** approved model artifact, feature schema, training dataset fingerprint, configuration and metrics.

### Application plane

1. **FastAPI service:** authentication, fleet, machine, observation, prediction, alert and work-order APIs.
2. **PostgreSQL:** users/roles, machine records, observations or replay references, predictions, alerts, work orders, model versions, policy versions and audit events.
3. **Inference service:** loads an approved model and matching preprocessing artifact; validates inputs and produces versioned outputs.
4. **Triage service:** deterministic policy engine; records input evidence, rule ID, severity, explanation and action.
5. **Work-order service:** idempotent creation, assignment, acknowledgement, status transitions and closure.
6. **React frontend:** fleet overview, machine detail, prediction history, alert queue, work-order workflow and model operations.

### MLOps plane

- MLflow experiment tracking.
- Model artifact and version metadata.
- Data / prediction quality monitoring.
- Scheduled or manually triggered offline retraining.
- Candidate evaluation and approval gate.
- Safe promotion and rollback.
- Audit trail of deployed model versions.

## 3. Runtime flow

`Dataset / Simulated Replay → Schema Validation → Feature Pipeline → RUL Model + Anomaly Detector → Prediction Persistence → Triage Policy → Alert / Work Order → Human Review → Dashboard`

The anomaly detector and RUL regressor are independent components. Triage combines their outputs according to an explicit policy; anomaly detection alone does not prove imminent failure.

## 4. Training flow

`Versioned Dataset → Data Audit → Engine-Aware Split → Train-Only Preprocessing Fit → Feature Construction → Baseline Models → Validation → Final Test Evaluation → Model Artifact + Metrics → Registration / Approval`

The test split remains untouched for final evaluation. The exact validation design will be finalized after examining FD001 and the competition's expected evaluation convention.

## 5. Failure handling

- Invalid schema or cycle sequence: reject the batch and report row/unit context.
- Missing required feature: do not silently substitute an arbitrary value; apply only a documented training-fitted preprocessing rule or reject.
- Inference error: persist an error state, create no automated maintenance action, and surface an operator-visible issue.
- Low-confidence / out-of-distribution input: mark prediction as requiring review.
- Duplicate event: use a stable event identity and database uniqueness to avoid duplicate predictions/actions.
- Triage service unavailable: preserve prediction and retry safely; never create an untraceable work order.
- Candidate model regression: do not promote; keep the current approved model.
- Database/API outage: fail visibly and retain retry-safe processing semantics.

## 6. Security and operational principles

- Use environment variables for secrets; commit only an `.env.example` with fake placeholders.
- Apply role-based authorization to maintenance actions.
- Log state changes and model/policy versions.
- Use parameterized database access and input validation.
- Keep the application advisory; do not control or shut down equipment.
- Make simulated data unmistakable in the interface.
