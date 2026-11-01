# FleetGuard — Complete System Workflow and Architecture

> **Document type:** End-to-end system architecture and implementation workflow  
> **Repository:** [Ayush-Kant/MachineDoc](https://github.com/Ayush-Kant/MachineDoc)  
> **Benchmark:** NASA C-MAPSS FD001  
> **Planning scope:** Phases 1–8  
> **Status:** Phase 1 research is documented in the repository. Phases 2–8 are implementation plans and must not be represented as implemented until their acceptance criteria are met.

---

## 1. Project overview

**FleetGuard** is a software-only predictive-maintenance and automated work-order management platform. It is designed to turn machine-cycle observations into traceable predictive insights and, where an explicit policy requires it, maintenance alerts and work orders that are reviewed by a human.

The initial proof of concept uses the **NASA Commercial Modular Aero-Propulsion System Simulation (C-MAPSS) FD001** turbofan-engine degradation benchmark. The project first establishes a reproducible data and machine-learning workflow, then builds an application around the resulting models.

FleetGuard is not simply an RUL prediction model. Its intended value is the complete workflow:

1. Ingest and validate engine-cycle measurements.
2. Build causal, per-engine time-series features.
3. Estimate Remaining Useful Life (RUL).
4. Independently assess unusual sensor behaviour.
5. Evaluate both outputs through a transparent, versioned triage policy.
6. Create traceable alerts and, where configured, pending-approval work orders.
7. Let managers and technicians review and complete maintenance work.
8. Record model, policy, event and user-action history.
9. Track experiments, model versions, deployment, monitoring and controlled retraining.

### 1.1 The problem FleetGuard addresses

Predictive-maintenance systems need more than a model output. A useful operational workflow must preserve the connection between the original observation, the derived features, model versions, prediction results, maintenance rules and human actions.

A standalone prediction can tell an analyst that an engine may have limited remaining life. It does not, by itself, explain:

- Which observations led to the prediction.
- Whether the incoming data was valid.
- Whether sensor behaviour was unusual independently of RUL.
- Which maintenance rule was triggered.
- Why an alert was created.
- Who reviewed or approved the resulting work.
- Which exact model and policy versions were involved.

FleetGuard is designed to make that chain explicit and auditable.

### 1.2 Project scope and evidence boundary

The initial system is a **benchmark-driven software proof of concept** based on simulated turbofan-engine degradation data.

- It is not connected to physical vehicles, aircraft, compressors, CAN buses or industrial sensors.
- C-MAPSS sensor columns remain identified by their generic names, such as **sensor_2** and **sensor_11**; no unsupported engineering names or units are invented.
- Simulated replay must be labelled visibly as simulated telemetry.
- RUL is an estimate, not a guaranteed failure countdown.
- An anomaly score is not proof of impending failure.
- RUL regression and anomaly detection remain separate components.
- Triage is advisory and deterministic; it does not control or shut down machinery.
- Operationally consequential work orders require human review.
- Real-world deployment claims require domain-specific validation that is outside the initial FD001 scope.

---

## 2. Project goals and success criteria

### 2.1 Engineering goals

| Area | Goal |
|---|---|
| Data engineering | Produce validated, reproducible and leakage-safe FD001 datasets and features. |
| RUL modelling | Train and compare regressors using engine-aware validation and documented metrics. |
| Anomaly assessment | Evaluate a separate anomaly detector without inventing unavailable ground-truth labels. |
| Backend | Provide authenticated APIs and reliable persistence for assets, observations, predictions and maintenance records. |
| Frontend | Provide fleet monitoring, asset details, prediction visualizations and maintenance workflows. |
| Triage | Convert model evidence into deterministic and explainable maintenance decisions. |
| Work orders | Prevent duplicate actions and require human approval before maintenance execution. |
| MLOps | Track experiments, register model versions, evaluate candidates and support safe promotion and rollback. |
| Deployment | Make the integrated application reproducible through documented containerized setup. |
| Submission | Present the system, methodology, evidence and limitations clearly. |

### 2.2 Definition of project success

The complete project is successful when:

- Raw input files are validated and processed reproducibly.
- Training and test RUL targets are derived according to the benchmark definition.
- Engine and temporal leakage are prevented.
- Models are compared using appropriate, recorded evaluation protocols.
- Predictions can be traced to an exact model and feature-schema version.
- RUL and anomaly outputs remain separate and correctly interpreted.
- Triage decisions include the policy version, matched rules and evidence.
- Reprocessing an event does not create duplicate alerts or work orders.
- Managers and technicians can complete the work-order workflow.
- Model candidates cannot replace the approved model without validation and approval.
- Invalid inputs and model failures fail visibly and safely.
- A clean environment can run the documented application and demonstration.
- All submission claims are supported by actual implementation or evaluation evidence.

---

## 3. Users and responsibilities

FleetGuard is planned around four application roles.

| Role | Main responsibilities | Typical access |
|---|---|---|
| Administrator | Manage users, asset registry, system configuration, model versions and policy activation. | System and model administration. |
| Maintenance manager | Monitor assets, review alerts, inspect triage evidence, approve/reject work orders and assign technicians. | Fleet and maintenance operations. |
| Technician | View assigned tasks, record inspection or maintenance notes and complete work orders. | Assigned work and relevant asset information. |
| Analyst | Review predictions, model evaluation, monitoring, model versions and triage history. | Read-oriented analytics and model information. |

Backend role enforcement is authoritative. Hiding a button in the frontend is not a security control.

---

## 4. Complete system architecture

FleetGuard is planned as a **modular monolith for the application layer**, supported by separate data/ML and MLOps workflows. This keeps the initial system understandable and testable without requiring a microservice architecture.

### 4.1 Logical architecture

The architecture has five major planes:

1. **Data plane:** source data, validation, target construction and feature engineering.
2. **ML plane:** training, evaluation, RUL regression, anomaly detection and inference artifacts.
3. **Application plane:** FastAPI, PostgreSQL, authentication, asset APIs and maintenance workflow.
4. **Decision and MLOps plane:** triage rules, event processing, experiment tracking, model registry and monitoring.
5. **Presentation plane:** React dashboard and role-specific interfaces.

~~~mermaid
flowchart TB
    subgraph DATA["1. DATA PLANE"]
        SRC["NASA C-MAPSS FD001<br/>train / test / RUL"]
        ING["Dataset adapter and ingestion"]
        VAL["Schema and data validation"]
        FEAT["Engine-aware causal feature pipeline"]
        MAN["Dataset manifest, feature schema<br/>and validation reports"]
        SRC --> ING --> VAL --> FEAT
        VAL --> MAN
        FEAT --> MAN
    end

    subgraph ML["2. MACHINE-LEARNING PLANE"]
        TRAIN["Training and experiment scripts"]
        RUL["RUL regression pipeline"]
        ANOM["Separate anomaly detector"]
        EVAL["Engine-aware validation<br/>and benchmark evaluation"]
        ART["Versioned model artifacts<br/>and inference contracts"]
        FEAT --> TRAIN
        TRAIN --> RUL
        TRAIN --> ANOM
        RUL --> EVAL
        ANOM --> EVAL
        EVAL --> ART
    end

    subgraph MLOPS["3. MLOPS PLANE"]
        MLFLOW["MLflow tracking server"]
        REG["Model registry"]
        GATE["Candidate evaluation<br/>and human approval gate"]
        DEPLOY["Approved model deployment<br/>and rollback"]
        MON["Data, prediction and<br/>operational monitoring"]
        TRAIN --> MLFLOW
        EVAL --> MLFLOW
        MLFLOW --> REG --> GATE --> DEPLOY
        MON --> GATE
    end

    subgraph APP["4. APPLICATION AND DECISION PLANE"]
        API["FastAPI modular application"]
        AUTH["Authentication and RBAC"]
        DB[("PostgreSQL")]
        INF["Inference adapter"]
        TRIAGE["Versioned deterministic<br/>triage policy engine"]
        OUTBOX["Transactional outbox<br/>and worker"]
        ALERT["Alerts and condition episodes"]
        WO["Work-order service"]
        AUDIT["Audit and event history"]
        API --> AUTH
        API <--> DB
        DEPLOY --> INF
        API --> INF
        INF --> DB
        INF --> TRIAGE
        TRIAGE --> DB
        TRIAGE --> OUTBOX
        OUTBOX --> ALERT
        OUTBOX --> WO
        ALERT --> DB
        WO --> DB
        API --> AUDIT
        WO --> AUDIT
        TRIAGE --> AUDIT
        MON <--> DB
    end

    subgraph UI["5. PRESENTATION PLANE"]
        WEB["React + TypeScript frontend"]
        DASH["Fleet and asset dashboards"]
        OPS["Alerts and work orders"]
        MODELUI["Model operations and monitoring"]
        WEB --> DASH
        WEB --> OPS
        WEB --> MODELUI
    end

    WEB <--> API
~~~

**Architecture interpretation:** the feature pipeline is shared by offline training and online/replay inference. RUL and anomaly models are independent. Their outputs are persisted and then evaluated by the policy engine. The policy engine does not retrain models or replace their predictions. MLflow manages the model lifecycle; PostgreSQL manages application and operational records.

### 4.2 Main component responsibilities

| Component | Responsibility | Must not do |
|---|---|---|
| Dataset adapter | Read supported benchmark files and preserve source identity. | Modify raw source files. |
| Validation layer | Check schema, values, identifiers, cycles and alignment. | Silently repair invalid data without a documented rule. |
| Feature pipeline | Create causal per-engine features with stable ordering. | Use future rows or cross-engine history. |
| RUL model | Estimate remaining cycles. | Claim an exact failure date. |
| Anomaly detector | Assess unusual feature/sensor behaviour. | Treat an anomaly as a confirmed failure. |
| Inference adapter | Load compatible approved artifacts and return versioned outputs. | Load arbitrary or unapproved models. |
| Triage engine | Apply deterministic rules and store decision evidence. | Hide decisions inside an opaque ML/LLM call. |
| Outbox worker | Retry reliable downstream action processing. | Create duplicate alerts/work orders. |
| Work-order service | Enforce workflow transitions and audit actions. | Automatically approve maintenance. |
| MLflow | Track experiments, artifacts and model versions. | Replace application records in PostgreSQL. |
| React frontend | Display data and invoke authorized APIs. | Implement authoritative triage or authorization logic. |

---

## 5. Data and benchmark foundation

### 5.1 Initial dataset

The first benchmark is NASA C-MAPSS **FD001**.

FD001 contains simulated turbofan-engine degradation trajectories under one operating condition and one fault mode (HPC degradation as documented in the project research baseline).

Each trajectory row has 26 numeric fields:

| Field group | Columns | Meaning |
|---|---:|---|
| Engine identifier | 1 | unit_id |
| Operating cycle | 1 | cycle |
| Operating settings | 3 | setting_1, setting_2, setting_3 |
| Sensor measurements | 21 | sensor_1 through sensor_21 |

The project uses generic sensor names. Engineering meanings and units must not be inferred without explicit source documentation.

### 5.2 Current Phase 1 audit findings

The structural audit documented the following:

| Audit item | Training | Testing |
|---|---:|---:|
| Rows | 20,631 | 13,096 |
| Columns | 26 | 26 |
| Engines | 100 | 100 |
| Engine IDs | 1–100 | 1–100 |
| Missing/non-finite values | 0 | 0 |
| Malformed/non-numeric rows | 0 | 0 |
| Exact duplicate rows | 0 | 0 |
| Per-engine cycles ordered and consecutive | Pass | Pass |
| Minimum trajectory length | 128 | 31 |
| Median trajectory length | 199 | 133.5 |
| Mean trajectory length | 206.31 | 130.96 |
| Maximum trajectory length | 362 | 303 |

The supplied test RUL vector contains 100 non-negative integer endpoint labels:

- Minimum: 7 cycles.
- Median: 86 cycles.
- Mean: 75.52 cycles.
- Maximum: 145 cycles.

The values align one-to-one with the 100 test engines in ascending ID order.

### 5.3 Sensor findings from Phase 1

Seven full columns are constant in FD001 training:

- setting_3
- sensor_1
- sensor_5
- sensor_10
- sensor_16
- sensor_18
- sensor_19

sensor_6 is near-constant, with only two observed training values (21.60 and 21.61).

Sensors with consistently increasing trends across all 100 training engines:

- sensor_2, sensor_3, sensor_4, sensor_8
- sensor_11, sensor_13, sensor_15, sensor_17

Sensors with consistently decreasing trends across all 100 training engines:

- sensor_7, sensor_12, sensor_20, sensor_21

sensor_9 has positive slopes in 71 engines and negative slopes in 29. sensor_14 has positive slopes in 60 and negative slopes in 40. Their pooled correlation is approximately +0.9632, so ablation experiments are planned rather than automatically deleting one.

The initial candidate sensor set is the 14 varying sensors other than near-constant sensor_6. This is a starting experiment, not a final feature selection.

### 5.4 Dataset handling and provenance

- Raw benchmark files must remain immutable.
- Preserve dataset identity, partition, engine ID and cycle throughout transformations.
- The training target is derived per engine.
- Supplied test RUL labels are evaluation ground truth, not inference inputs.
- Preprocessing and feature selection are fitted on training engines only.
- The official test set remains sealed until the final evaluation protocol is frozen.
- Dataset manifests should record source identity, file checksums, schema and pipeline version.

**Repository hygiene item:** the current repository tree contains train_FD001.txt, test_FD001.txt and RUL_FD001.txt at the root, while project documentation says raw NASA data should not be committed. This inconsistency must be reviewed against applicable source terms before a final public release. Do not delete or alter source files blindly.

---

## 6. RUL definition and target construction

RUL is the number of additional operating cycles remaining after the currently observed cycle, up to the simulated failure endpoint.

### 6.1 Training target

For training engine u, let C_max,u be its final run-to-failure cycle. At observed cycle c:

~~~text
RUL_train(u, c) = C_max,u - c
~~~

This calculation must be performed separately for each engine. Do not subtract a global maximum cycle.

Example: training engine 1 has 192 observations and ends at cycle 192.

| Current cycle | RUL |
|---:|---:|
| 1 | 191 |
| 96 | 96 |
| 191 | 1 |
| 192 | 0 |

### 6.2 Test target

Test trajectories are truncated; their final observed cycle is not the failure cycle.

For test engine u, let:

- C_last,u = final observed test cycle.
- RUL_final,u = supplied RUL label for that engine.
- c = current observed cycle.

Then:

~~~text
RUL_test(u, c) = (C_last,u - c) + RUL_final,u
~~~

At the final observed test row, c = C_last,u, so the target is exactly the supplied endpoint label.

For test engine 1, the last observed cycle is 31 and the supplied endpoint RUL is 112. Its derived RUL at cycle 1 is 142; at cycle 31 it is 112.

**Leakage rule:** the supplied test RUL vector must never enter model input features. It is used for benchmark evaluation only.

### 6.3 Capped and uncapped targets

Phase 3 will compare:

- Uncapped RUL targets.
- A separately documented capped target experiment (a cap of 125 cycles was proposed for comparison, but is not a raw-data property and must be justified).

The original derived target and the model training target must remain distinguishable.

---

## 7. End-to-end runtime workflow

The complete operational path is:

~~~mermaid
flowchart TD
    A["Import supported trajectory or start labelled replay"]
    B["Validate schema, numeric values, engine identity and cycle ordering"]
    C{"Input valid?"}
    D["Reject or quarantine input<br/>record quality issue"]
    E["Persist observation and stable event identity"]
    F["Build causal per-engine features"]
    G["Load compatible approved RUL model"]
    H["Load compatible approved anomaly detector"]
    I["Generate RUL estimate"]
    J["Generate independent anomaly assessment"]
    K["Persist both predictions and exact model versions"]
    L["Evaluate active triage policy"]
    M{"Policy requires action?"}
    N["Record no-action / monitor decision"]
    O["Persist triage evidence and create outbox event"]
    P["Outbox worker processes event idempotently"]
    Q["Create or update alert / condition episode"]
    R{"Policy requires work order?"}
    S["No work order"]
    T["Create pending-approval work order"]
    U["Manager reviews and approves/rejects"]
    V["Assignment and technician workflow"]
    W["Completion, audit history and dashboard update"]

    A --> B --> C
    C -- No --> D
    C -- Yes --> E --> F
    F --> G --> I
    F --> H --> J
    I --> K
    J --> K
    K --> L --> M
    M -- No --> N
    M -- Yes --> O --> P --> Q --> R
    R -- No --> S --> W
    R -- Yes --> T --> U --> V --> W
~~~

### 7.1 Input and ingestion

A supported source is either:

- An offline FD001 trajectory import.
- A row or sequence emitted by the deterministic simulator/replay.

Every ingestion path must pass the same validation and persistence contract. A simulator must not bypass validation by writing directly to prediction or maintenance tables.

### 7.2 Validation

Validate:

- Required schema and field order.
- Numeric and finite sensor/setting values.
- Engine identity and dataset/partition identity.
- Cycle uniqueness and ordering.
- Missing or unexpected required fields.
- Feature-schema compatibility where inference is requested.
- Event identity and duplicate ingestion.

Reject or quarantine invalid records with useful error context. Do not invent missing values or silently alter the source.

### 7.3 Feature generation

The feature pipeline groups records by engine and sorts by cycle. Every feature at cycle c may use only observations at c or earlier.

The exact Phase 2 feature design is described in Section 11.

### 7.4 Independent inference

The inference adapter loads an approved RUL pipeline and an approved anomaly detector independently. It verifies artifact identity, feature schema and feature ordering.

RUL returns a prediction in cycles. The anomaly detector returns its own score and, when validated, a threshold-based status. The outputs must not be merged into one opaque model score.

### 7.5 Persistence and traceability

Persist:

- Source event and observation identity.
- Asset and dataset identity.
- Prediction timestamp.
- RUL prediction.
- Anomaly score/status.
- RUL model version.
- Anomaly model version.
- Feature-schema version.
- Data-quality state.
- Triage decision and policy version, when evaluated.

### 7.6 Maintenance decision

The triage engine evaluates the prediction evidence and produces an explicit decision. If an operational action is required, it emits an idempotent outbox event for alert and work-order processing.

Human approval remains required before work execution.

---

## 8. Separate offline training workflow

Training and online/replay inference use the same feature definitions but have different data boundaries.

~~~mermaid
flowchart TD
    A["Versioned raw FD001 files"]
    B["Structural and data-quality audit"]
    C["Training RUL construction"]
    D["Engine-aware train / validation / confirmation split"]
    E["Fit preprocessing on training engines only"]
    F["Causal feature construction"]
    G["Train baseline and candidate RUL models"]
    H["Train separate anomaly candidates"]
    I["Grouped validation and truncated-history evaluation"]
    J["RUL metrics and residual analysis"]
    K["Synthetic-corruption and clean-data anomaly evaluation"]
    L{"Candidate meets evaluation and compatibility gates?"}
    M["Record rejected candidate and findings"]
    N["Serialize model + preprocessing + feature schema"]
    O["Track run, data fingerprint, config and artifacts in MLflow"]
    P["Register candidate model version"]
    Q["Human approval and controlled promotion"]

    A --> B --> C --> D --> E --> F
    F --> G --> I
    F --> H --> I
    I --> J
    I --> K
    J --> L
    K --> L
    L -- No --> M
    L -- Yes --> N --> O --> P --> Q
~~~

### Training safeguards

- All rows from one engine stay in the same engine-level split.
- Fit preprocessing only on training engines.
- Do not use unit_id as an ordinary predictive sensor feature.
- Preserve unit_id and cycle for traceability and ordering.
- Evaluate cycle as an optional elapsed-age feature through ablation.
- Never use future readings to create an earlier-cycle feature.
- Keep test RUL labels out of inference features.
- Compare model candidates using the same validation protocol.
- Do not repeatedly tune against the official test labels.

---

## 9. Phase roadmap at a glance

FleetGuard is divided into eight sequential phases.

| Phase | Name | Main output | Status at document creation |
|---:|---|---|---|
| 1 | Problem understanding and research | Dataset audit, target definition, sensor findings and scope | Research baseline documented |
| 2 | Reproducible data engineering | Validated, split and feature-engineered FD001 datasets | Planned |
| 3 | Machine learning | Evaluated RUL and anomaly artifacts with reports | Planned |
| 4 | Backend and persistence | FastAPI, PostgreSQL, authentication and APIs | Planned |
| 5 | Frontend | React dashboard and maintenance workflows | Planned |
| 6 | Triage and MLOps | Deterministic policies, idempotent actions and model lifecycle | Planned |
| 7 | Integration and deployment | Tested, containerized, deployable application | Planned |
| 8 | Competition submission | One-page overview, diagrams, report, presentation and demo | Planned |

~~~mermaid
flowchart LR
    P1["1. Research<br/>Scope and evidence"]
    P2["2. Data engineering<br/>Validated features"]
    P3["3. ML<br/>Evaluated models"]
    P4["4. Backend<br/>APIs and database"]
    P5["5. Frontend<br/>User workflows"]
    P6["6. Triage + MLOps<br/>Decisions and lifecycle"]
    P7["7. Integration<br/>Deployment and E2E"]
    P8["8. Submission<br/>Evidence and demo"]

    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8
~~~

Each phase has an explicit exit gate. A phase should not be marked complete merely because its code exists; its outputs and acceptance tests must be verified.

---

# PART I — PHASE-BY-PHASE IMPLEMENTATION PLAN

## 10. Phase 1 — Problem understanding and research

**Goal:** Establish the benchmark, target definition, evidence boundary and engineering requirements before implementation.

### 10.1 Work completed and documented

The current repository contains the Phase 1 research baseline:

- docs/project-charter.md
- docs/dataset-guide.md
- docs/system-architecture.md
- docs/ml-methodology.md
- docs/phase1-findings-and-decisions.md
- docs/rul-targets-and-examples.md
- docs/audits/fd001-data-audit.md
- docs/audits/fd001-sensor-behaviour-analysis.md
- scripts/inspect_fd001.py
- scripts/analyze_fd001_sensors.py
- reports/phase1/ sensor metrics and correlation outputs

### 10.2 Key decisions established

- Start with FD001 and expand to FD002–FD004 only after the FD001 pipeline and evaluation are reproducible.
- Keep RUL regression and anomaly detection separate.
- Use engine-aware splits, not random row splits.
- Fit preprocessing on training data only.
- Compare capped and uncapped targets rather than silently assuming a cap.
- Preserve unit_id and cycle for traceability.
- Keep generic sensor identifiers and do not invent sensor units.
- Clearly label any replay as simulated.
- Require transparent, auditable, human-reviewed maintenance actions.

### 10.3 Phase 1 exit gate

The research baseline is considered complete when dataset structure, RUL derivation, data integrity, initial sensor behaviour, leakage risks, scope and next-phase experiment requirements are documented.

---

## 11. Phase 2 — Reproducible data engineering

**Goal:** Build a deterministic pipeline that converts raw FD001 files into validated model-ready feature sets and separate evaluation labels.

### 11.1 Technology

- Python 3.11+ as the proposed project environment.
- Pandas and NumPy for tabular and time-series processing.
- PyArrow/Parquet for typed intermediate and processed datasets.
- Scikit-learn utilities where appropriate.
- Pytest for validation and leakage tests.
- TOML configuration for benchmark settings.

Exact versions will be pinned after the environment is tested.

### 11.2 Planned module layout

~~~text
src/fleetguard/
    data/
        schema.py
        loaders.py
        validation.py
        targets.py
        splitting.py
        pipeline.py
    features/
        temporal.py
        build.py

configs/
    fd001.toml

scripts/
    run_phase2.py

tests/
    unit/
    integration/

data/
    raw/             # Local source data; not committed by default
    interim/         # Generated intermediate files
    processed/
        fd001/
~~~

### 11.3 Input and validation contract

The loader should support the existing root-level file arrangement and the intended local data/raw arrangement through an explicit input directory/configuration.

Validation checks include:

- Required 26-column schema.
- Numeric and finite values.
- Engine ID and cycle integrity.
- Unique engine-cycle keys.
- Consecutive ordered cycles where expected.
- One-to-one alignment of test engines and RUL endpoint labels.
- Dataset file checksums and provenance.
- Immutable raw input files.

### 11.4 Planned feature strategy

Initial candidate inputs:

- 14 varying sensors, excluding near-constant sensor_6 from the baseline.
- setting_1 and setting_2.
- Optional sensor_6 ablation.
- Optional cycle as an elapsed-age feature, tested separately.

Causal temporal features to compare:

| Feature family | Proposed construction |
|---|---|
| Current reading | Current-cycle value for selected sensors |
| Rolling mean | Windows of 5 and 10 cycles |
| Rolling standard deviation | Windows of 5 and 10 cycles |
| Recent difference | Current value minus previous cycle |
| Recent trend | Linear slope over the trailing 10 cycles |
| Early baseline deviation | Current value relative to the first 10-cycle per-engine baseline |

For rolling windows, use complete windows (minimum periods equal to the window length) in the initial design. Preserve warm-up NaNs; do not fill them with arbitrary zero values or silently drop early rows.

The initial candidate set is approximately 115 columns when optional near-constant sensor_6 is included:

- 14 candidate sensor readings.
- 2 operating settings.
- Optional sensor_6.
- 28 rolling means (14 sensors × 2 windows).
- 28 rolling standard deviations.
- 14 recent differences.
- 14 trailing slopes.
- 14 baseline-deviation features.

This is a candidate schema, not a final approved feature list. Phase 3 ablations decide which groups are retained.

### 11.5 Split and processed-output plan

A provisional split plan is:

- 80 training engines for model development.
- 20 separate engines reserved for confirmation.
- Seed 42 as an initial reproducibility setting.
- Five-fold GroupKFold within the 80 development engines during Phase 3.

The final engine IDs, split seed and validation details must be saved in the manifest and frozen before model comparisons.

Planned outputs:

~~~text
data/processed/fd001/
    train_features.parquet
    train_targets.parquet
    test_features.parquet
    evaluation_only/
        test_endpoint_labels.parquet
    metadata/
        dataset_manifest.json
        feature_schema.json
        validation_report.json
        engine_split.json
~~~

Features and targets are stored separately. The test endpoint labels are explicitly evaluation-only and never enter the model input matrix.

### 11.6 Leakage and reproducibility tests

- No engine appears in both train and held-out engine groups.
- No feature uses future-cycle values.
- Changing future readings does not change earlier features.
- Rolling calculations never cross engine boundaries.
- Feature order and names are stable.
- RUL formulas are checked against worked examples.
- Re-running the pipeline produces the same logical outputs and manifest.
- Existing output replacement is controlled and safe.

### 11.7 Phase 2 exit gate

A single documented command should reproduce the processed datasets, reports and split metadata from immutable raw files. All schema, target, grouping, temporal-leakage and idempotency tests must pass.

**Not in Phase 2:** model training, FastAPI, React, PostgreSQL, MLflow, anomaly-model selection and cloud deployment.

---

## 12. Phase 3 — Machine learning

**Goal:** Train, compare and evaluate RUL regressors and anomaly detectors using the Phase 2 data contract.

### 12.1 RUL modelling candidates

Start with simple baselines:

- Training-target mean/median predictor.
- Cycle-only diagnostic baseline.
- Ridge regression with preprocessing fitted inside a pipeline.
- RandomForestRegressor.
- HistGradientBoostingRegressor.
- Optional XGBoost only if its installation, license and reproducibility are justified.
- Sequence models such as LSTM/CNN only if classical models provide a clear baseline and there is time to justify the added complexity.

Do not select a model solely by training score.

### 12.2 Validation protocol

The planned validation should emulate the real benchmark task: predict RUL at the last observed cycle of an engine whose future trajectory is not available to inference.

Proposed experiment:

1. Split training engines into development and reserved confirmation groups.
2. Use grouped folds inside the development group.
3. Create truncated observed histories at 50%, 65% and 80% of each validation engine's trajectory.
4. Use 65% as the primary planned cutoff and the others as secondary robustness checks.
5. Calculate the target from the known training endpoint, but do not expose the endpoint or future readings as features.
6. Keep the 20 confirmation engines separate from candidate selection.
7. Freeze decisions before one final official test evaluation.

The precise cutoff construction and split IDs must be recorded and checked during implementation.

### 12.3 RUL metrics

Report:

- MAE.
- RMSE.
- NASA asymmetric score.
- Median absolute error.
- 90th percentile absolute error.
- Bias.
- Underprediction/overprediction counts.
- Predictions within defined cycle tolerances.
- Error by RUL band.
- Per-engine residuals and fold stability.

For the NASA asymmetric score, let d = prediction - actual. The planned convention is:

~~~text
If d < 0: score contribution = exp(-d / 13) - 1
If d >= 0: score contribution = exp(d / 10) - 1

Total score = sum of contributions over evaluated engines
~~~

Lower is better. The exact implemented convention must be unit-tested against the documented benchmark definition.

Compare uncapped and capped targets (including a documented cap experiment such as 125 only if justified). Report the target formulation with every result.

### 12.4 Feature ablations

Compare:

- Raw selected sensor values.
- Adding operating settings.
- Adding cycle.
- Sensor_9 and sensor_14 separately and together.
- Sensor_6 inclusion/exclusion.
- Rolling means and standard deviations.
- Recent difference and slope.
- Early-baseline deviation.
- Combined feature set.

Ablation decisions must be based on engine-aware validation, not pooled row correlations alone.

### 12.5 Anomaly detection

No row-level ground-truth anomaly labels are supplied in FD001.

Evaluate anomaly detection separately using:

- Robust median/MAD reference statistics.
- IsolationForest as a candidate.
- Explicit synthetic corruptions on controlled validation trajectories.

Planned synthetic corruption categories:

- Isolated spike.
- Persistent offset.
- Gradual drift.
- Sensor freeze.
- Noise burst.

Each injected event must have a scenario ID, seed, sensor, start/end cycle, corruption magnitude and label.

Report precision, recall, F1, PR-AUC/ROC-AUC only where the labelled synthetic evaluation supports them, false-positive rate on unmodified data, false alerts per 1,000 clean observations and detection delay.

Thresholds are calibrated on calibration/validation data, not the final held-out test.

Do not claim industrial anomaly accuracy from synthetic corruptions.

### 12.6 Model artifacts and inference contracts

RUL and anomaly artifacts must be independently serialized and versioned. Include:

- Model and preprocessing artifact.
- Feature schema/version and ordering.
- Training dataset fingerprint.
- Training configuration.
- Evaluation metrics and report.
- Code commit and dependency information.
- Artifact checksum.

The inference output should include engine/asset identity, latest cycle, RUL estimate, anomaly score/status separately, model versions, feature schema version, timestamp and data-quality status.

Clamp a negative RUL estimate to zero only for a clearly documented display/business rule; preserve the raw model output for diagnostics. Do not show uncertainty unless calibrated and validated.

### 12.7 Phase 3 exit gate

A selected candidate must have reproducible training, leakage-safe validation, documented comparison with baselines, separate anomaly evaluation, compatible serialized artifacts, a stable inference contract and a recorded final benchmark evaluation.

---

## 13. Phase 4 — Backend and persistence

**Goal:** Build the authenticated application backend and persistent store around the Phase 2/3 contracts.

### 13.1 Architecture choice

Use a FastAPI modular monolith with synchronous SQLAlchemy sessions as the initial design. This is sufficient for the expected prototype workload and avoids unnecessary async database complexity.

Proposed stack:

- FastAPI.
- SQLAlchemy 2.x.
- PostgreSQL.
- Psycopg 3.
- Alembic migrations.
- Pydantic v2 and Pydantic Settings.
- JWT bearer authentication.
- Argon2 password hashing.
- Pytest and HTTPX for API tests.

Versions must be verified and pinned during implementation.

### 13.2 Planned backend layout

~~~text
backend/
    app/
        core/
        db/
        models/
        schemas/
        api/
        services/
        integrations/
        utils/
    migrations/
    tests/
    scripts/
~~~

### 13.3 Planned database entities

| Table | Responsibility |
|---|---|
| users | User accounts and role assignment |
| assets | Asset/engine identity and metadata |
| observations | Validated cycle measurements |
| ingestion_batches | Batch import and validation history |
| model_versions | Application-facing model metadata |
| rul_predictions | RUL results and model references |
| anomaly_assessments | Independent anomaly results |
| alerts | Maintenance alert records |
| work_orders | Maintenance work-order state |
| work_order_events | Work-order transition history |
| audit_events | Security and operational audit trail |

Asset uniqueness must include dataset and partition identity as well as unit_id, because engine identifiers can repeat between train and test partitions.

Observations should be uniquely identified by asset and cycle (with an explicit schema/version strategy). JSONB may store validated sensor measurements, with indexed relational columns for important query keys. RUL predictions and anomaly assessments remain distinct.

### 13.4 Planned work-order state machine

~~~mermaid
stateDiagram-v2
    [*] --> pending_approval
    pending_approval --> approved: Manager approves
    pending_approval --> rejected: Manager rejects
    pending_approval --> cancelled: Authorized cancellation

    approved --> assigned: Assign technician
    approved --> cancelled: Authorized cancellation

    assigned --> in_progress: Technician starts
    assigned --> cancelled: Authorized cancellation

    in_progress --> completed: Completion remarks recorded
    in_progress --> cancelled: Authorized cancellation

    rejected --> [*]
    cancelled --> [*]
    completed --> [*]
~~~

Every transition must be validated by the backend and recorded with actor, timestamp, previous/new state and relevant reason/remarks. Rejection requires a reason; completion requires completion remarks.

### 13.5 Idempotency

A repeated request with the same idempotency key and same payload should return the original result. Reusing the key with a different payload should produce a conflict. Database uniqueness constraints protect against concurrent duplicate requests.

### 13.6 API groups

Planned endpoint groups:

- Health: /health/live, /health/ready.
- Authentication: /api/v1/auth/token, /api/v1/auth/me.
- Users: user management and technician lookup.
- Assets: list, create, detail and status.
- Observations: batch ingestion, history, latest and cycle range.
- Predictions: RUL inference/history/latest and anomaly inference/history/latest.
- Alerts: list, detail, acknowledge, resolve and dismiss.
- Work orders: create/list/detail, approve/reject, assign, status transitions and events.
- Dashboard: summary and recent activity.

The Phase 5 UI will require explicit summary/recent-activity endpoints and a manager/admin technician lookup endpoint. These must be included in the Phase 4 API implementation rather than aggregated inefficiently in the browser.

### 13.7 Inference integration

The backend must load approved model artifacts and matching preprocessing once at startup or controlled reload. It verifies artifact checksum, feature schema and feature ordering. RUL and anomaly failures are independent: one should not silently be represented as a successful result from the other.

### 13.8 Authentication decision to settle

The initial design considered a short-lived JWT access token. Before implementation, settle the browser session strategy. Possible options include an in-memory access token requiring re-login after reload, or a secure HttpOnly refresh-cookie design with appropriate CSRF protection. Do not store long-lived credentials in browser localStorage by default. Apply backend authorization regardless of the frontend choice.

### 13.9 Phase 4 exit gate

Migrations, authentication, role authorization, API contracts, persistence, inference adapter, work-order transitions, audit trail, error handling and PostgreSQL-backed tests must work.

**Not in Phase 4:** automated triage policy decisions, MLOps promotion workflow, and Phase 6 outbox-driven automatic work-order generation.

---

## 14. Phase 5 — Frontend

**Goal:** Provide the user-facing application for fleet visibility, asset details, predictions, alerts and work-order management.

### 14.1 Technology

- React + TypeScript.
- Vite.
- Tailwind CSS v4.
- React Router.
- TanStack Query for server state.
- Axios central API client.
- Recharts.
- React Hook Form and Zod.
- Lucide icons.
- Vitest and React Testing Library.
- MSW for API mocks.
- Playwright for browser E2E tests.

Do not introduce Redux by default. Authentication context and local component state are enough for the initial application; TanStack Query manages server state.

### 14.2 Planned frontend layout

~~~text
frontend/
    public/
    src/
        app/
        layouts/
        components/
            ui/
            navigation/
            tables/
            charts/
            feedback/
        features/
            auth/
            dashboard/
            assets/
            observations/
            predictions/
            alerts/
            work-orders/
            users/
        pages/
        lib/
            api/
            query/
            constants/
            utils/
        hooks/
        types/
        styles/
    tests/
        unit/
        components/
        integration/
        e2e/
~~~

### 14.3 Main routes

~~~text
/login
/app/overview
/app/assets
/app/assets/:assetId
/app/alerts
/app/alerts/:alertId
/app/work-orders
/app/work-orders/new
/app/work-orders/:workOrderId
/app/my-tasks
/app/admin/users
/app/403
/*
~~~

### 14.4 Role-based navigation

| Role | Planned navigation |
|---|---|
| Administrator | Overview, Assets, Alerts, Work Orders, User Management |
| Manager | Overview, Assets, Alerts, Work Orders |
| Technician | Overview, My Assigned Tasks, Assets, Work Orders |
| Analyst | Overview, Assets, Predictions, Alerts; model metrics after Phase 6 |

Frontend route guards improve user experience, but the backend remains the authorization authority.

### 14.5 Main pages

**Overview dashboard**

- Total assets.
- Active assets.
- Assets with predictions.
- Open alerts.
- Open work orders.
- RUL distribution.
- Asset table.
- Recent alerts.
- Recent work orders.

Do not fabricate a fleet-health percentage or display sample values as live data.

**Asset list and details**

- Search, filter, pagination and sorting.
- Asset identity and dataset/partition labels.
- Overview and sensor history.
- Prediction history and observations.
- Maintenance/work-order history.

**Sensor charts**

Use sensor identifiers exactly as provided. Do not assign unsupported physical units or names. Avoid plotting every sensor on one shared unscaled axis.

**Prediction charts**

Show RUL in cycles and clearly label it as a model estimate. Show anomaly score separately and document its score direction/meaning.

**Alerts**

Support filtering, detail view, evidence, acknowledge/resolve/dismiss actions according to backend permissions.

**Work orders**

Support creation where authorized, manager approval/rejection/assignment, technician task handling, status transitions, timeline and completion remarks.

### 14.6 UI and accessibility

- Persistent simulated-data banner.
- Clear loading, empty, error and unauthorized states.
- Confirmation dialogs for consequential actions.
- Keyboard accessibility and visible focus.
- Readable charts and text summaries.
- Responsive desktop/tablet/mobile layout.
- Server-side pagination where applicable.
- No fake zeros or placeholder records presented as actual data.

### 14.7 Phase 5 exit gate

Authentication, API integration, role-based navigation, dashboard, assets, predictions, alerts, work orders, responsive layout, accessibility, tests and production build must work against the Phase 4 API contract.

**Not in Phase 5:** triage rule execution, automated work-order generation, MLflow lifecycle and telemetry simulator control.

---

## 15. Phase 6 — Triage and MLOps

**Goal:** Connect model outputs to deterministic maintenance decisions and introduce a controlled model lifecycle.

Phase 6 has two workstreams: operational triage and MLOps.

### 15.1 Triage input contract

The policy evaluator receives structured evidence:

- Asset and source-event identity.
- Dataset/partition identity.
- Latest cycle.
- Predicted RUL.
- Anomaly score and status (if calibrated).
- Data-quality status.
- RUL model version.
- Anomaly model version.
- Feature-schema version.
- Prediction timestamp.
- Active policy version.

Test RUL labels and other evaluation-only data are not policy inputs.

### 15.2 Triage output contract

Every evaluation produces a record, including when no action is required:

- Decision ID and asset ID.
- Source event and evaluation identity.
- Decision (no_action, monitor, inspection, maintenance_review or equivalent documented vocabulary).
- Severity and priority.
- Matched rules.
- Human-readable explanation.
- Exact values/thresholds used as evidence.
- RUL, anomaly and feature-schema versions.
- Policy version.
- Human-review requirement.
- Evaluation timestamp.

### 15.3 Triage rule design

Use a deterministic Python evaluator driven by immutable, versioned configuration. Do not use an LLM or another opaque model to decide whether to create a work order.

Initial decision matrix:

| RUL assessment | Anomaly assessment | Initial interpretation |
|---|---|---|
| Healthy | Normal | Continue monitoring |
| Warning | Normal | Maintenance review may be appropriate |
| Critical | Normal | High-priority maintenance review |
| Healthy | Elevated | Inspect unusual sensor/operating behaviour |
| Warning | Elevated | Increase inspection priority |
| Critical | Elevated | Highest configured review priority |
| Invalid/unavailable | Any | Data/inference issue; no automatic maintenance action |

Exact thresholds must be established only after Phase 3 results and replay evaluation. The matrix is a policy design, not a claim that FD001 validates real-world maintenance boundaries.

### 15.4 Policy versioning

Policy files are versioned and immutable after activation. A policy update produces a new version, not an in-place edit.

A policy includes:

- Policy ID and version.
- Dataset/application scope.
- RUL warning and critical boundaries.
- Anomaly thresholds and score direction.
- Alert/work-order action mapping.
- Clear/hysteresis thresholds.
- Activation status.
- Approval identity and timestamp.

A historical decision continues to reference the exact policy version that produced it.

### 15.5 Event and action idempotency

Use two identities:

1. **Evaluation identity:** identifies evaluation of a source event with specific model and policy versions.
2. **Operational condition identity:** identifies the maintenance condition/episode for which an alert or work order exists.

A policy/model update can create a new evaluation record without automatically opening a duplicate work order for an existing condition.

Use database constraints as the final duplicate protection. Application-level checks alone are not enough for concurrent requests.

### 15.6 Transactional outbox

~~~mermaid
sequenceDiagram
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Worker as Outbox Worker
    participant Alert as Alert Service
    participant WO as Work-order Service

    API->>DB: Persist prediction and triage decision
    API->>DB: Insert outbox event in same transaction
    DB-->>API: Transaction committed
    Worker->>DB: Fetch pending event
    Worker->>Alert: Create/update alert episode
    Alert->>DB: Persist alert with uniqueness checks
    Worker->>WO: Create work order if policy requires
    WO->>DB: Create pending-approval work order idempotently
    Worker->>DB: Mark event processed
    Note over Worker,DB: On failure, retry safely; uniqueness prevents duplicate actions
~~~

This protects against a crash between storing a decision and creating its downstream operational action. A PostgreSQL-polling worker is sufficient for the first release; Kafka/Celery/microservices are not required.

### 15.7 Alert flapping and episodes

Use separate activation and clearing thresholds where appropriate. Keep an active condition episode until its documented clearing condition is met. Do not suppress a genuine severity escalation merely because a cooldown is active.

### 15.8 Triage rollout modes

| Mode | Behaviour |
|---|---|
| disabled | No triage evaluation/action processing |
| shadow | Store decisions; create no alerts/work orders |
| alerts_only | Create alerts; do not create automatic work orders |
| approval_required | Create alerts and work orders in pending_approval |

Start in shadow mode, inspect deterministic replay scenarios, move to alerts-only and enable pending-approval work-order creation only after reliability tests pass.

### 15.9 MLOps with MLflow

Create separate tracked experiments:

- fleetguard-rul-fd001
- fleetguard-anomaly-fd001
- fleetguard-rul-evaluation
- fleetguard-anomaly-evaluation

Log:

- Model algorithm and hyperparameters.
- Target formulation and RUL cap.
- Ordered features and schema version.
- Preprocessing.
- Dataset fingerprint and split IDs.
- Random seed.
- Evaluation metrics.
- Git commit.
- Dependency/environment metadata.
- Model artifacts, reports, plots and prediction samples.

Use separate registered models for RUL and anomaly detection. Use explicit aliases such as candidate and champion rather than relying on deprecated stage concepts. Every prediction stores the exact version that was used; it must not rely on a mutable alias for historical traceability.

### 15.10 Candidate evaluation and promotion

A candidate must pass:

- Feature-schema and artifact checks.
- Leakage checks.
- Comparable engine-aware evaluation.
- RUL metric and tail-error guardrails.
- Anomaly threshold and false-alert checks.
- Serialization and inference smoke tests.
- Compatibility checks.
- Human approval.

Do not repeatedly tune candidates using official test labels. Candidate selection uses validation/confirmation data; official test evaluation remains a distinct benchmark step.

### 15.11 Safe deployment and rollback

- Load the candidate separately from the active model.
- Validate artifact, schema and smoke-test predictions.
- Record the deployment attempt.
- Switch the active reference only after successful validation.
- Preserve the prior known-good version.
- On rollback, verify the old artifact before switching.
- Record the actor, reason, exact versions and deployment history.

A failed candidate must not replace the current working model.

### 15.12 Monitoring

Monitor four categories:

**Input quality:** missingness, non-finite values, cycle gaps/order, duplicate events, schema mismatches, stale records and feature distribution changes.

**RUL behaviour:** prediction distribution, drift in prediction statistics, abrupt changes, negative raw outputs, model version, latency and errors.

**Anomaly behaviour:** score distribution, fraction flagged, trends by sensor/feature and review outcomes where available.

**Application operations:** inference failures, alerts per window, work orders created, outbox backlog/retries, pending approvals and workflow completion/rejection counts.

Because FD001 does not provide continuous real operational labels, do not display live model accuracy/MAE for unlabelled replay data. Behaviour monitoring is not the same as ground-truth model performance monitoring.

### 15.13 Controlled retraining

Start with manual retraining. The workflow is:

1. Administrator requests a training job.
2. Dataset manifest and configuration are validated.
3. Phase 2 builds eligible features/targets.
4. Phase 3 training/evaluation runs.
5. MLflow records the run.
6. Candidate is registered.
7. Evaluation gate compares with champion.
8. Administrator approves/rejects promotion.

Unlabelled replay data must not be treated as supervised RUL training data.

### 15.14 Planned Phase 6 database additions

Extend the Phase 4 schema with:

| Table | Purpose |
|---|---|
| triage_policies | Immutable policy versions and approval metadata |
| triage_decisions | Complete evaluation and evidence history |
| alert_episodes | Lifecycle of continuous conditions |
| outbox_events | Retryable downstream events |
| model_deployments | Deployment and rollback history |
| monitoring_snapshots | Aggregated monitoring observations |

Add relevant policy/decision/model references to alerts and work orders. Reconcile migrations with the actual Phase 4 schema before implementing.

### 15.15 Planned Phase 6 APIs

| Endpoint | Purpose |
|---|---|
| GET /api/v1/triage/policies | List policies |
| GET /api/v1/triage/policies/{policyId} | Policy detail |
| GET /api/v1/triage/decisions | Decision history |
| GET /api/v1/triage/decisions/{decisionId} | Decision evidence |
| POST /api/v1/triage/simulate | Dry-run policy evaluation |
| POST /api/v1/triage/policies/{policyId}/activate | Activate approved policy |
| GET /api/v1/model-operations/overview | Deployed model status |
| GET /api/v1/models | Registered models |
| GET /api/v1/models/{modelName}/versions | Model versions |
| GET /api/v1/models/{modelName}/evaluations | Evaluation details |
| GET /api/v1/model-deployments | Deployment history |
| POST /api/v1/models/{modelName}/versions/{version}/promote | Request promotion |
| POST /api/v1/models/{modelName}/rollback | Request rollback |
| POST /api/v1/training-jobs | Start controlled training |
| GET /api/v1/training-jobs/{jobId} | Training status |
| GET /api/v1/monitoring/summary | Monitoring overview |
| GET /api/v1/monitoring/data-quality | Data-quality statistics |
| GET /api/v1/monitoring/predictions | Prediction trends |
| GET /api/v1/monitoring/anomalies | Anomaly trends |
| GET /api/v1/monitoring/operations | Operational metrics |

The worker should call internal services directly rather than making unnecessary HTTP requests back into its own API.

### 15.16 Planned Phase 6 frontend additions

- **Model Operations:** active/candidate versions, metrics, promotion and rollback.
- **Model Monitoring:** input quality, prediction/anomaly distributions, latency and failures.
- **Triage Policy Management:** active version, thresholds, rules and dry-run preview.
- **Decision Explorer:** evidence, matched rules, model/policy versions and linked alert/work order.

The first policy editor should remain configuration-driven. Avoid building a complex visual rule builder before there is a need.

### 15.17 Phase 6 exit gate

MLflow tracking/registry, candidate evaluation, deployment/rollback, deterministic triage, policy versioning, idempotent alert/work-order generation, outbox recovery, monitoring, secured APIs, UI and end-to-end failure tests must work.

---

## 16. Phase 7 — Integration and deployment

**Goal:** Run the complete application as one reproducible system and prove the complete workflow in a clean environment.

### 16.1 Deployment architecture

The initial deployment target is one Linux VM with Docker Compose. Kubernetes, distributed event brokers and multi-region architecture are outside the first release.

Planned services:

- Reverse proxy (Nginx or Caddy).
- React production frontend.
- FastAPI backend.
- PostgreSQL.
- MLflow tracking server.
- Outbox worker.
- Persistent model/artifact storage.

~~~mermaid
flowchart TB
    USER["User browser"]
    PROXY["Nginx / Caddy reverse proxy<br/>HTTPS and route handling"]

    subgraph HOST["Single Linux host / VM"]
        subgraph PRIVATE["Private application network"]
            FE["React static frontend"]
            API["FastAPI backend"]
            WORKER["Outbox worker"]
            DB[("PostgreSQL volume")]
            MLFLOW["MLflow service"]
            ART["Persistent artifact storage"]
        end
    end

    USER -->|HTTPS| PROXY
    PROXY -->|/| FE
    PROXY -->|/api| API
    API <--> DB
    API --> ART
    API --> MLFLOW
    MLFLOW --> ART
    WORKER <--> DB
~~~

Only the reverse proxy should be publicly exposed. PostgreSQL, MLflow, worker and internal artifact paths stay on private networks or protected administration paths.

### 16.2 Containerization

Use Dockerfiles for backend and frontend. The frontend uses a multi-stage build: Node build stage, then a small static-serving runtime. Backend images install pinned dependencies, run non-root and exclude local datasets/caches.

Planned infrastructure files:

~~~text
Dockerfile
compose.yaml
compose.production.yaml
.dockerignore

backend/
    Dockerfile

frontend/
    Dockerfile

infra/
    nginx/
        nginx.conf
    postgres/
        init/
~~~

Exact paths may be reconciled with the Phase 4/5 application structure.

### 16.3 Compose services, health and persistence

Use service-level health checks and health-aware startup dependencies. Startup order alone does not prove a database or tracking server is ready.

Persistent volumes are required for:

- PostgreSQL records.
- MLflow artifacts.
- Approved model artifacts where stored separately.
- Backups outside the ephemeral container filesystem.

Separate development and production configuration. Publicly expose only the reverse proxy.

### 16.4 Initialization and demo seeding

A clean startup procedure should:

1. Wait for PostgreSQL readiness.
2. Apply Alembic migrations.
3. Safely create/verify the first administrator.
4. Load demo users and simulated assets only through an explicit idempotent seed command.
5. Verify required model artifacts and schema compatibility.
6. Start API, worker and frontend.
7. Perform health and smoke checks.

Demo data must not expose test RUL labels to inference.

### 16.5 Environment and security

Use .env.example for safe placeholders and keep .env out of Git.

Configure application environment, database URL, JWT secret, CORS origins, MLflow URI, artifact storage, model names, public domain and demo mode through environment settings.

Never expose secrets in Vite frontend environment variables. Do not expose PostgreSQL or MLflow administrative interfaces publicly. Use HTTPS, restricted CORS, secure authentication, backend role enforcement, non-root containers and sanitized logs.

### 16.6 CI/CD

Use GitHub Actions for pull-request and main-branch validation.

Planned workflows:

**Backend:** install locked dependencies, lint/type check, unit tests and PostgreSQL integration tests.

**Frontend:** npm ci, lint, TypeScript checks, component/unit tests and production build.

**Full stack:** start PostgreSQL/services, apply migrations, run API integration tests and Playwright E2E tests.

**Deployment:** build immutable images tagged by commit/release, deploy only after checks pass, apply migrations, run health checks and retain the previous known-good release.

Protect deployment secrets through environment-scoped configuration and explicit approval where needed. Do not deploy every experimental branch to the public demo.

### 16.7 Simulated telemetry replay

Build a deterministic replay service with:

| Mode | Purpose |
|---|---|
| single_step | Advance one observation for inspection/debugging |
| accelerated | Replay faster than real time for demonstration |
| continuous | Replay at a configured interval |

Controls should include dataset/partition, engine, start/pause/resume, speed, current cycle, progress and reset.

Replay event identity should be stable, for example:

~~~text
dataset_id + partition + engine_id + cycle
~~~

Replay uses the normal ingestion/validation path. It must not bypass feature generation or directly fabricate persisted predictions. Any synthetic corruption used for a specific demo must be identified and labelled as synthetic.

### 16.8 Observability and recovery

Structured logs should include timestamp, service, level, request/correlation ID, asset/event ID where relevant, model version, policy version and result. Do not log passwords, tokens or secrets.

Health checks should cover API liveness/readiness, database readiness, model availability, MLflow response, proxy routing and worker progress/outbox backlog.

Document and test:

- PostgreSQL backup and restore.
- Model artifact retention and backup.
- Container restart behaviour.
- Worker retry behaviour.
- Model rollback.
- Application image rollback.
- Database restoration into a separate test environment.

### 16.9 End-to-end verification

Required scenarios:

1. Clean install and migration.
2. Demo-data seeding and repeat seeding.
3. Authentication and role authorization.
4. Observation ingestion and validation.
5. Feature generation and model inference.
6. Independent RUL/anomaly persistence.
7. Triage decision and evidence.
8. Alert and work-order generation once.
9. Manager approval and technician completion.
10. Duplicate-event replay.
11. Candidate model promotion and failed deployment.
12. Model rollback.
13. Database/worker restart and recovery.
14. Deployment health checks and backup restoration.

### 16.10 Phase 7 exit gate

A second developer can follow the instructions in a clean environment, start the system, run the demo workflow and understand its limits without manually repairing the setup. All end-to-end, security, persistence, recovery and deployment checks are documented.

---

## 17. Phase 8 — Competition submission and demonstration

**Goal:** Present the completed FleetGuard implementation and its actual evidence in a concise, credible and technically understandable submission.

The official competition brief takes precedence over the suggested formats below. Page limits, slide limits, video duration, naming and submission rules must be checked before preparing the final package.

### 17.1 Submission deliverables

| Deliverable | Purpose |
|---|---|
| One-page project overview | Explain the problem, solution, architecture and proof quickly |
| Architecture diagram | Explain system components and data/control flows |
| Technical report | Document design, methodology, implementation and evaluation |
| Presentation deck | Tell the case-study story |
| Live demo or video | Demonstrate the complete application |
| Evidence package | Support metrics, reliability and implementation claims |
| Repository README | Provide reproducible setup and project overview |

### 17.2 One-page overview

Suggested hierarchy:

1. Project name and concise tagline.
2. Problem and proposed solution.
3. Central architecture diagram.
4. ML methodology and application workflow.
5. Actual model/evaluation metrics.
6. Real application screenshot or demo link/QR.
7. Small limitations/scope statement.

If the competition does not prescribe a page size, A4 landscape is a useful option for a wide architecture diagram. Keep the page concise; the report carries detailed explanation.

Do not use illustrative or placeholder metrics in the final submission.

### 17.3 Architecture diagram deliverables

Create two diagrams from the same architecture source:

- Detailed engineering diagram for the technical report.
- Simplified five-zone diagram for the one-page overview and presentation.

Zones: data, ML, application, decision/MLOps and presentation. Show the RUL and anomaly components separately, and include the alert/work-order human-review path.

Keep editable vector source and export SVG/PDF. Do not try to fit every Python module or database column into the high-level diagram.

### 17.4 Technical report structure

1. Executive summary.
2. Problem and motivation.
3. Benchmark and dataset analysis.
4. RUL definition and target construction.
5. Data engineering and leakage safeguards.
6. ML methods and evaluation.
7. Application architecture.
8. Triage and work-order workflow.
9. MLOps and deployment.
10. Results and system testing.
11. Limitations and future scope.
12. Conclusion and references.

Include actual results only. Explain validation protocol, dataset split, target formulation, metrics and model version for every metric table.

### 17.5 Presentation deck

Suggested 8–10 slide narrative, adjusted to official limits:

1. FleetGuard title and one-line solution.
2. Problem and why predictions alone are insufficient.
3. Complete solution workflow.
4. System architecture.
5. Data and ML methodology.
6. Model evaluation and real results.
7. Triage and maintenance workflow.
8. MLOps, monitoring and reliability.
9. Demonstration.
10. Impact, limitations and next steps.

Each slide should communicate one main idea. Use actual screenshots and consistent architecture visuals.

### 17.6 Demonstration storyline

A suggested 4–5 minute demonstration (adjust to competition time limit):

1. Dashboard and simulated-data scope.
2. Fleet overview and asset selection.
3. Sensor history and latest observation.
4. RUL prediction and separate anomaly assessment.
5. Triage decision with matched rules and evidence.
6. Alert and pending-approval work order.
7. Manager approval and technician workflow.
8. Model version, monitoring and decision traceability.
9. Closing summary.

Use deterministic demo data and a prepared scenario. Record a backup video and capture screenshots. Never fabricate outputs or manually alter data just to make the demo look successful.

### 17.7 Evidence-to-claim mapping

| Claim | Required evidence |
|---|---|
| RUL estimation works | Actual held-out predictions and evaluation report |
| Feature generation is leakage-safe | Tests for temporal and engine isolation |
| Model beats baseline | Comparable validation results |
| Anomaly detector finds synthetic corruptions | Scenario-labelled synthetic evaluation and clean false-alert results |
| Triage is explainable | Decision records with matched rules/evidence |
| Work orders are idempotent | Duplicate and concurrent event tests |
| Human review is enforced | API authorization and workflow tests |
| Model versions are traceable | MLflow registry and persisted prediction versions |
| Rollback works | Deployment/rollback tests |
| Full application works | E2E report and demonstration |
| Deployment is reproducible | Clean deployment logs, health and recovery results |

### 17.8 Repository and data hygiene

Before final release:

- Resolve the discrepancy between the current committed raw FD001 files and documentation saying raw data should not be committed. Verify the applicable source terms; do not delete files blindly.
- Ensure no credentials, .env, local databases or unintended model binaries are tracked.
- Make setup and test commands reproducible.
- Update README with architecture, data handling, evaluation, screenshots, setup, deployment, tests, limitations and attribution.
- Ensure every feature marked implemented actually exists and is tested.
- Verify repository and demo links.
- Check exported PDF and slides on another device or clean environment.

### 17.9 Phase 8 exit gate

A reviewer can understand FleetGuard, inspect its implementation, evaluate the evidence, follow the limitations and see the main workflow demonstrated. The package follows the official competition submission requirements.

---

# PART II — DATA MODEL, SECURITY AND OPERATING RULES

## 18. Planned data model overview

The Phase 4 operational entities and Phase 6 additions are linked conceptually as follows. The final schema will be implemented through migrations and refined against actual query patterns.

~~~mermaid
erDiagram
    USERS ||--o{ WORK_ORDERS : assigned_to
    USERS ||--o{ WORK_ORDER_EVENTS : performs
    USERS ||--o{ AUDIT_EVENTS : creates
    DATASETS ||--o{ ASSETS : contains
    ASSETS ||--o{ OBSERVATIONS : has
    ASSETS ||--o{ RUL_PREDICTIONS : receives
    ASSETS ||--o{ ANOMALY_ASSESSMENTS : receives
    ASSETS ||--o{ ALERT_EPISODES : has
    ASSETS ||--o{ ALERTS : raises
    ASSETS ||--o{ WORK_ORDERS : requires
    RUL_PREDICTIONS ||--o{ TRIAGE_DECISIONS : informs
    ANOMALY_ASSESSMENTS ||--o{ TRIAGE_DECISIONS : informs
    TRIAGE_POLICIES ||--o{ TRIAGE_DECISIONS : evaluates
    TRIAGE_DECISIONS ||--o{ ALERTS : explains
    TRIAGE_DECISIONS ||--o{ WORK_ORDERS : triggers
    ALERTS ||--o{ WORK_ORDERS : sources
    WORK_ORDERS ||--o{ WORK_ORDER_EVENTS : records
    MODEL_VERSIONS ||--o{ RUL_PREDICTIONS : produces
    MODEL_VERSIONS ||--o{ ANOMALY_ASSESSMENTS : produces
    MODEL_DEPLOYMENTS }o--|| MODEL_VERSIONS : deploys
    OUTBOX_EVENTS }o--o| TRIAGE_DECISIONS : references

    USERS {
        uuid id PK
        string email
        string password_hash
        string role
    }
    DATASETS {
        uuid id PK
        string dataset_name
        string partition
        string fingerprint
    }
    ASSETS {
        uuid id PK
        uuid dataset_id FK
        int unit_id
        string status
    }
    OBSERVATIONS {
        uuid id PK
        uuid asset_id FK
        int cycle
        json measurements
        string schema_version
    }
    MODEL_VERSIONS {
        uuid id PK
        string model_name
        string version
        string artifact_uri
        string feature_schema_version
    }
    RUL_PREDICTIONS {
        uuid id PK
        uuid asset_id FK
        uuid model_version_id FK
        float predicted_rul
        datetime predicted_at
    }
    ANOMALY_ASSESSMENTS {
        uuid id PK
        uuid asset_id FK
        uuid model_version_id FK
        float anomaly_score
        string assessment
    }
    TRIAGE_POLICIES {
        uuid id PK
        string policy_id
        string version
        string status
    }
    TRIAGE_DECISIONS {
        uuid id PK
        uuid policy_id FK
        string decision
        json evidence
        string source_event_id
    }
    ALERTS {
        uuid id PK
        uuid asset_id FK
        uuid decision_id FK
        string severity
        string status
    }
    ALERT_EPISODES {
        uuid id PK
        uuid asset_id FK
        string condition_key
        string status
    }
    WORK_ORDERS {
        uuid id PK
        uuid asset_id FK
        uuid decision_id FK
        uuid assigned_user_id FK
        string status
    }
    WORK_ORDER_EVENTS {
        uuid id PK
        uuid work_order_id FK
        string event_type
        datetime occurred_at
    }
    AUDIT_EVENTS {
        uuid id PK
        uuid user_id FK
        string action
        datetime occurred_at
    }
    OUTBOX_EVENTS {
        uuid id PK
        string event_type
        string status
        int attempt_count
    }
    MODEL_DEPLOYMENTS {
        uuid id PK
        uuid model_version_id FK
        string status
        datetime deployed_at
    }
~~~

**Note:** this is a conceptual relationship diagram, not an exact SQLAlchemy schema. Some entities (for example, dataset identity) may be represented through existing metadata or separate tables depending on the Phase 4 implementation. Migrations must match the final implementation.

---

## 19. Key safety and reliability invariants

These rules apply across every phase and must remain true in the final application.

### 19.1 Data integrity

- Raw files remain immutable.
- Every observation retains dataset, partition, engine and cycle identity.
- Test RUL labels never enter inference features.
- Train/validation separation is by engine.
- Every temporal feature is causal.
- Preprocessing is fitted on training data only.
- Feature order and schema are versioned.

### 19.2 Model integrity

- RUL and anomaly models remain separate.
- Every inference result references exact model version(s).
- Model artifacts are checked for integrity and schema compatibility.
- Candidate models are evaluated before promotion.
- Previous approved versions remain available for rollback.
- Unlabelled telemetry is not treated as labelled RUL data.
- Accuracy/performance is not claimed without suitable ground truth.

### 19.3 Operational integrity

- Every triage decision stores matched rules and evidence.
- Every decision references exact policy and model versions.
- Duplicate events cannot create duplicate operational actions.
- Work orders created by policy begin pending human approval.
- State transitions are validated by the backend.
- User actions are audited.
- Invalid input or inference failure must not create an automated maintenance action.
- Outbox retries are safe.

### 19.4 Security

- Backend RBAC is authoritative.
- Passwords are securely hashed.
- Secrets are environment-managed and never committed.
- Database and MLflow are not publicly exposed by default.
- Frontend build variables contain no secrets.
- Logs do not expose passwords, tokens or API keys.
- Administrative model/policy operations are restricted.
- User inputs and API payloads are validated.

### 19.5 Product honesty

- The UI labels simulated telemetry persistently.
- Predictions are estimates, not guaranteed failure dates.
- Anomaly scores are not equivalent to confirmed faults.
- Generic sensor names stay generic.
- No physical-machine integration or certification is claimed.
- Synthetic anomaly test performance is clearly identified as synthetic.

---

## 20. Proposed final repository structure

The target structure below combines all eight phases. It is a planned structure, not a claim that these folders already exist.

~~~text
MachineDoc/
│
├── README.md
├── workflow.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── configs/
│   ├── fd001.toml
│   └── triage/
│       └── fd001/
│           └── policy-v1.toml
│
├── data/
│   ├── raw/                  # Local only; not committed by default
│   ├── interim/              # Generated
│   └── processed/            # Generated
│
├── src/
│   └── fleetguard/
│       ├── data/
│       ├── features/
│       ├── models/
│       ├── inference/
│       ├── triage/
│       ├── mlops/
│       └── monitoring/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   ├── integrations/
│   │   ├── utils/
│   │   └── workers/
│   ├── migrations/
│   ├── tests/
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   ├── layouts/
│   │   ├── components/
│   │   ├── features/
│   │   ├── pages/
│   │   ├── lib/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── styles/
│   ├── tests/
│   └── Dockerfile
│
├── scripts/
│   ├── inspect_fd001.py
│   ├── analyze_fd001_sensors.py
│   ├── run_phase2.py
│   ├── train_rul.py
│   ├── train_anomaly.py
│   ├── evaluate_candidate.py
│   ├── run_tracked_training.py
│   ├── run_outbox_worker.py
│   └── load_demo_data.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── reports/
│   ├── phase1/
│   ├── phase2/
│   ├── phase3/
│   ├── phase6/
│   ├── phase7/
│   └── phase8/
│
├── docs/
│   ├── project-charter.md
│   ├── dataset-guide.md
│   ├── system-architecture.md
│   ├── ml-methodology.md
│   ├── phase1-findings-and-decisions.md
│   ├── rul-targets-and-examples.md
│   ├── audits/
│   ├── decisions/
│   ├── evaluation/
│   ├── deployment-guide.md
│   ├── operations-guide.md
│   └── submission/
│
├── infra/
│   ├── nginx/
│   └── postgres/
│
├── Dockerfile
├── compose.yaml
├── compose.production.yaml
└── .github/
    └── workflows/
~~~

Do not create every directory at the beginning. Introduce folders when the corresponding phase is implemented, and avoid empty modules or duplicate implementations.

---

## 21. Key implementation sequence and dependencies

| Order | Work package | Depends on | Exit proof |
|---:|---|---|---|
| 1 | Phase 2 data pipeline | Phase 1 research | Reproducible validated features/targets |
| 2 | Phase 3 RUL/anomaly experiments | Phase 2 outputs | Evaluation reports and compatible artifacts |
| 3 | Phase 4 backend | Phase 2/3 contracts | Tested APIs and persistent records |
| 4 | Phase 5 frontend | Phase 4 OpenAPI contract | Role-based user workflows |
| 5 | Phase 6A MLOps | Phase 3 model artifacts | Tracking, registry, promotion and rollback |
| 6 | Phase 6B triage | Phase 4/5 and model outputs | Explainable and idempotent maintenance workflow |
| 7 | Phase 7A local integration | Phase 2–6 | Compose-based full-stack run |
| 8 | Phase 7B release/deployment | 7A | Public deployment, health checks and recovery |
| 9 | Phase 8 submission | Verified implementation/evidence | Report, diagrams, presentation and demo |

A later phase may identify a defect in an earlier contract. Fix the upstream contract and its tests rather than adding a workaround that creates a second source of truth.

---

## 22. Phase acceptance checklist

This is the master completion checklist. A phase is complete only after its exit evidence is available.

- [x] **Phase 1 — Research baseline:** dataset audit, RUL target understanding, sensor behaviour, scope and baseline decisions documented.
- [ ] **Phase 2 — Data engineering:** reproducible ingestion, validation, causal features, targets, engine splits and tests.
- [ ] **Phase 3 — Machine learning:** baseline comparison, RUL evaluation, separate anomaly evaluation and model artifacts.
- [ ] **Phase 4 — Backend:** authenticated APIs, PostgreSQL persistence, inference adapter and work-order state machine.
- [ ] **Phase 5 — Frontend:** dashboard, asset views, predictions, alerts, work orders, roles and tests.
- [ ] **Phase 6 — Triage/MLOps:** policy decisions, idempotency, outbox, MLflow, promotion, monitoring and rollback.
- [ ] **Phase 7 — Integration/deployment:** Docker Compose, HTTPS, CI/CD, simulator replay, E2E, backup and recovery.
- [ ] **Phase 8 — Submission:** one-page overview, architecture diagrams, report, presentation, demo and evidence audit.

---

## 23. Existing project documents and supporting references

The following repository documents are the detailed Phase 1 source of truth. This workflow document connects them to the planned future implementation.

| Document | Why it matters |
|---|---|
| [Project charter](docs/project-charter.md) | Problem, scope, roles, workflow and risks |
| [Dataset guide](docs/dataset-guide.md) | Source files, raw schema, target and handling rules |
| [System architecture](docs/system-architecture.md) | Initial logical architecture and failure handling |
| [ML methodology](docs/ml-methodology.md) | Candidate models, evaluation and inference contract |
| [Phase 1 findings](docs/phase1-findings-and-decisions.md) | Research results and decisions |
| [RUL targets and examples](docs/rul-targets-and-examples.md) | Exact training/test RUL derivation |
| [FD001 data audit](docs/audits/fd001-data-audit.md) | Structural validation and dataset statistics |
| [Sensor behaviour analysis](docs/audits/fd001-sensor-behaviour-analysis.md) | Trend, variation and correlation evidence |

### External dataset references

- [NASA Prognostics Center of Excellence Data Set Repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/)
- [NASA Open Data — C-MAPSS Jet Engine Simulated Data](https://catalog.data.gov/dataset/cmapss-jet-engine-simulated-data)
- Saxena, Goebel, Simon and Eklund, “Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation,” 2008 International Conference on Prognostics and Health Management: [DOI 10.1109/PHM.2008.4711414](https://doi.org/10.1109/PHM.2008.4711414).

Check and follow applicable source terms before redistributing benchmark files.

---

## 24. Final system statement

FleetGuard is planned as a reproducible predictive-maintenance software platform that connects:

**Validated sensor data → causal feature engineering → independent RUL and anomaly models → explainable deterministic triage → alerts and human-reviewed work orders → model monitoring and controlled lifecycle management.**

The project is deliberately phased so that every layer has a defined contract, tests and acceptance criteria before the next layer depends on it.

The first benchmark remains NASA C-MAPSS FD001. The first deployment remains a software-only demonstration. Any expansion to real machinery, different datasets or safety-critical use requires new data, domain validation, risk analysis and explicit scope approval.

**Implementation principle:** build and verify each phase in dependency order, preserve evidence for every claim, and never mark a planned capability as completed until it works and has been tested.
