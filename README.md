# FleetGuard

**Predictive Maintenance and Automated Work Order Management**

FleetGuard is a software-only predictive-maintenance platform built around the NASA C-MAPSS turbofan engine degradation benchmark. It prepares sensor time series, detects anomalous operating behaviour, estimates Remaining Useful Life (RUL), applies transparent rule-based maintenance triage, and manages maintenance work orders.

> **Scope and evidence boundary:** The initial proof of concept uses the simulated C-MAPSS turbofan benchmark. It is not connected to physical vehicles or industrial machinery. Any live telemetry shown in demonstrations must be labelled as simulated. Predictions are estimates and must not be presented as guarantees of failure.

## Project objectives

1. Build a reproducible data-ingestion and validation pipeline.
2. Engineer time-series features without leakage across engines or time.
3. Evaluate anomaly-detection and RUL-regression approaches using appropriate held-out data.
4. Serve approved model predictions through a backend API.
5. Provide a fleet and machine monitoring interface.
6. Convert prediction outputs into explainable, bounded maintenance recommendations.
7. Create idempotent work orders with human review and status tracking.
8. Track experiments, model versions, monitoring results and controlled retraining.

## Initial dataset scope

Start with **FD001** from the NASA C-MAPSS dataset. Expand to FD002–FD004 only after the FD001 pipeline and evaluation are reproducible.

The original raw files are space-delimited text with 26 fields per row:
- Engine/unit identifier
- Operating cycle
- Three operational settings
- 21 sensor measurements

Training trajectories run to failure. Test trajectories stop before failure and are accompanied by a per-engine final RUL label.

## Repository structure (planned)

```text
MachineDoc/
├── README.md
├── docs/
│   ├── project-charter.md
│   ├── dataset-guide.md
│   ├── system-architecture.md
│   ├── ml-methodology.md
│   ├── decisions/
│   └── evaluation/
├── data/
│   ├── raw/                 # Local only; do not commit NASA data
│   ├── interim/             # Local only; generated
│   └── processed/           # Local only; generated
├── notebooks/               # Exploratory analysis, not production pipeline
├── src/
│   └── fleetguard/
│       ├── data/
│       ├── features/
│       ├── models/
│       ├── inference/
│       ├── triage/
│       └── monitoring/
├── backend/
├── frontend/
├── tests/
├── scripts/
├── configs/
├── artifacts/                # Local model outputs; do not commit by default
├── .gitignore
└── requirements.txt
```

The structure is a target layout, not a claim that these components have already been implemented.

## Proposed technology stack

| Area | Initial choice |
|---|---|
| Language and data | Python, Pandas, NumPy |
| Modelling | Scikit-learn |
| Experiment tracking | MLflow |
| API | FastAPI |
| Database | PostgreSQL |
| Frontend | React, Tailwind CSS |
| Charts | Recharts |
| Tests | Pytest |
| Packaging | Docker |
| Version control | Git and GitHub |

Dependencies and versions will be pinned after the environment is created and tested.

## Development phases

1. **Problem understanding and research** — inspect source files, understand the benchmark, define RUL, document assumptions and finalize acceptance criteria.
2. **Data engineering** — ingest, validate, profile, clean and transform FD001; create engine-aware features and target labels.
3. **Machine learning** — establish baselines, train and compare RUL models, evaluate anomaly detection, document metrics and register the selected model.
4. **Backend** — design persistence and APIs for machines, observations, predictions, alerts and work orders.
5. **Frontend** — implement fleet overview, machine details, predictions, alerts and maintenance workflows.
6. **Triage and MLOps** — implement deterministic decision rules, idempotent work-order creation, experiment/model tracking and controlled retraining.
7. **Integration and deployment** — test end-to-end paths, failure handling, reproducibility and containerized setup.
8. **Competition submission** — prepare architecture, methodology, evidence, demo script and presentation.

## Engineering principles

- Prevent train/test leakage. Split and validate at engine level where appropriate.
- Never use test ground-truth RUL as a model input.
- Fit preprocessing transforms on training data only.
- Keep raw benchmark files immutable.
- Preserve engine and cycle identifiers through every transformation.
- Report metrics on the prescribed test-engine endpoints as well as any validation protocol we define.
- Treat anomaly detection and RUL estimation as separate outputs; an anomaly is not automatically a failure.
- Keep triage deterministic, auditable, bounded and reversible.
- Require human acknowledgement/approval for operationally consequential actions.
- Do not retrain on unlabelled operational data as though it had ground-truth RUL.
- Do not commit datasets, model binaries, credentials, local databases or environment files.

## Data source and attribution

Primary source: [NASA Prognostics Center of Excellence Data Set Repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/).

Dataset catalogue: [NASA C-MAPSS Jet Engine Simulated Data](https://catalog.data.gov/dataset/cmapss-jet-engine-simulated-data).

Reference paper: A. Saxena, K. Goebel, D. Simon, and N. Eklund, “Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation,” 2008 International Conference on Prognostics and Health Management. [https://doi.org/10.1109/PHM.2008.4711414](https://doi.org/10.1109/PHM.2008.4711414).

Verify and follow applicable source terms before redistributing dataset files. The repository will not contain the raw dataset.

## Current status

- [x] Repository initialized with project overview.
- [x] Phase 1: dataset and problem investigation (dataset audit, RUL derivation, sensor behaviour and baseline decisions documented).
- [ ] Phase 2: reproducible FD001 data pipeline.
- [ ] Phase 3: evaluated ML models.
- [ ] Phase 4: backend and persistence.
- [ ] Phase 5: frontend.
- [ ] Phase 6: triage and MLOps.
- [ ] Phase 7: integration and deployment.
- [ ] Phase 8: competition submission.

Phase 1 working documents:
- [Phase 1 findings and decisions](docs/phase1-findings-and-decisions.md)
- [FD001 structural audit](docs/audits/fd001-data-audit.md)
- [FD001 sensor behaviour analysis](docs/audits/fd001-sensor-behaviour-analysis.md)
- [FD001 RUL targets and worked examples](docs/rul-targets-and-examples.md)
- [Dataset guide](docs/dataset-guide.md)
- [Reproducible sensor analysis script](scripts/analyze_fd001_sensors.py)
- [Phase 1 sensor analysis outputs](reports/phase1/)

See the `docs/` directory for detailed project specifications as they are added.
