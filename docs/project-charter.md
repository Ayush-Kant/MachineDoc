# FleetGuard Project Charter

## 1. Problem statement

Operators of connected machinery need earlier indications of degradation so they can plan inspections and maintenance rather than relying only on breakdowns or fixed service intervals. FleetGuard demonstrates a software workflow that consumes machine-cycle measurements, estimates Remaining Useful Life (RUL), flags unusual behaviour, and creates traceable maintenance work orders under explicit rules.

## 2. Benchmark and scope

The initial benchmark is NASA's Commercial Modular Aero-Propulsion System Simulation (C-MAPSS) turbofan engine degradation dataset. Begin with FD001.

Important boundary: C-MAPSS is a simulated turbofan-engine benchmark. The initial project is a benchmark-driven software proof of concept, not a validated truck, bus, compressor, or real aircraft engine monitoring product.

### In scope for the first complete version

- Offline ingestion and validation of the original FD001 train, test and RUL files.
- Reproducible exploratory data analysis.
- Engine-aware feature engineering and target construction.
- A leakage-conscious validation approach.
- RUL regression model baselines and comparison.
- A separate anomaly-detection experiment.
- Batch inference and a clearly labelled simulated telemetry demonstration.
- Rule-based triage with transparent reasons.
- Idempotent maintenance work-order creation and human workflow.
- API, database, web dashboard, testing, model tracking and deployment documentation.

### Out of scope unless separately agreed

- Direct connection to real vehicles, CAN buses, industrial sensors or maintenance systems.
- Claims of certified or safety-critical predictive capability.
- Automatic control of machinery or shutdown.
- Claims that C-MAPSS's 21 sensor names map directly to generic truck/bus/compressor telemetry.
- Autonomous retraining or promotion of a model without evaluation and approval.

## 3. Users and roles

- **Administrator:** manages users, machine registry, system configuration and model versions.
- **Maintenance manager:** monitors fleet health, reviews alerts, prioritizes and assigns work orders.
- **Technician:** views assigned work, records inspection/maintenance outcomes and closes work orders.
- **Analyst:** reviews model outputs, evaluation evidence and monitoring information.

## 4. Primary end-to-end workflow

1. An authorized user imports a supported engine trajectory or starts the labelled simulator.
2. The ingestion layer validates schema, numeric values, engine identity and cycle ordering.
3. The feature pipeline creates per-engine historical features without mixing trajectories.
4. The model service returns an RUL estimate and the anomaly service returns its own score/flag.
5. A versioned triage policy evaluates the outputs and records the rule and evidence used.
6. A work order is created only when the policy says so; a deterministic idempotency key prevents duplicates.
7. A human reviews, assigns, acknowledges and closes the work order.
8. The system stores observations, predictions, model version, policy version and user actions for traceability.
9. Monitoring supports data-quality, prediction and model-performance review.
10. Retraining is a controlled offline workflow using eligible labelled data, followed by validation and explicit model promotion.

## 5. Success criteria

The project is successful when:

- Raw input files are validated and processed reproducibly.
- RUL labels for train and test data are derived according to the documented benchmark definition.
- All data splitting and preprocessing avoid leakage.
- Models are compared using appropriate metrics and a recorded protocol.
- Predictions can be reproduced from a registered model version.
- Triage decisions are explainable and auditable.
- Repeated processing of the same event does not create duplicate work orders.
- Users can review and update work-order state.
- Invalid input and model failures fail safely.
- Tests and local setup instructions allow another developer to reproduce the demonstration.

## 6. Key risks and mitigations

| Risk | Mitigation |
|---|---|
| Train/test leakage | Keep test data sealed until final evaluation; split validation by engine. |
| Misinterpreting RUL | Document row-level target calculation and test endpoint scoring separately. |
| Sensor noise | Profile distributions and temporal traces; do not remove true degradation. |
| Anomaly confused with failure | Keep anomaly score and RUL estimate separate in UI and triage. |
| Unlabelled new data used for supervised retraining | Require eligible labels and explicit dataset version. |
| Duplicate work orders | Idempotency key and database uniqueness constraint. |
| Model regression | Evaluate candidate against baseline and retain previous approved model. |
| Simulated telemetry mistaken for real | Persistent UI labels and documentation. |
| Domain overclaim | State limits of the C-MAPSS benchmark and absence of physical validation. |

## 7. Decisions to confirm during Phase 1

- Exact raw file format, column order and readme details from the downloaded archive.
- Which sensors contain informative variation in FD001.
- RUL target cap: compare uncapped and capped formulations rather than assume one.
- Validation protocol and metrics.
- Anomaly detection input representation and threshold calibration.
- Operational semantics for converting benchmark cycle data into the simulated fleet workflow.
- Final API contract and database schema before backend implementation.
