# FleetGuard Phase 1 — Research Findings and Baseline Decisions

**Status:** Research and requirements baseline completed  
**Scope:** FD001 benchmark, RUL target definition, data quality, sensor degradation behaviour, modelling constraints and next-phase plan.

## 1. What Phase 1 established

- The competition problem is Remaining Useful Life prediction for a fleet of simulated turbofan engines.
- The initial dataset is FD001: one operating condition (documented as sea level) and one fault mode (HPC degradation).
- The exact train, test and RUL files are present on the project's main branch and have been read from their exact Git blob contents.
- Both trajectory files contain 26 numeric columns: unit ID, cycle, three operating settings and 21 sensors.
- Training trajectories run to simulated failure; testing trajectories stop early and have one supplied endpoint RUL label per engine.
- The training and test files have 100 engines each; the structural audit found 20,631 training rows and 13,096 test rows.
- RUL target derivation is now documented and checked with real examples.
- Sensor trend, consistency, distribution and inter-sensor correlation analyses have been completed.

## 2. Dataset quality and target decisions

See:
- [FD001 structural audit](audits/fd001-data-audit.md)
- [RUL targets and worked examples](rul-targets-and-examples.md)
- [Dataset guide](dataset-guide.md)

The target formula for a training row is:

`RUL(u,c) = C_{max,u} - c`

The supplied test RUL value belongs to the final observed row for each test engine. For a prior observed cycle, the descriptive row-level value is:

`RUL(u,c) = (C_{last,u} - c) + RUL_{final,u}`

The test RUL file must not be used as an inference feature. It is ground truth for benchmark evaluation.

## 3. Sensor analysis findings

See [FD001 sensor behaviour analysis](audits/fd001-sensor-behaviour-analysis.md).

### Consistent directional signals

Across all 100 training engines, the following sensors had a positive linear slope and an increase between first and last 10% window means:

- sensor_2, sensor_3, sensor_4, sensor_8
- sensor_11, sensor_13, sensor_15, sensor_17

Across all 100 training engines, the following had a negative linear slope and a decrease between first and last 10% window means:

- sensor_7, sensor_12, sensor_20, sensor_21

These 12 sensors are strong initial candidates, not a proven final feature list.

### Inconsistent or weak signals

- sensor_9: positive slope in 71 engines and negative slope in 29.
- sensor_14: positive slope in 60 engines and negative slope in 40.
- sensor_6: only two unique values; a high normalized-stage correlation reflects a very small numerical change and must not be mistaken for strong signal.

### Constant channels

The six constant sensor columns are sensor_1, sensor_5, sensor_10, sensor_16, sensor_18 and sensor_19. The constant operating setting is setting_3. These have no variation in FD001 training and should be excluded from the first FD001 model's predictive inputs. Preserve all original columns in source files and schema documentation.

### Redundancy

The largest correlation between varying sensor channels is sensor_9 / sensor_14 (approximately +0.963). Other moderately high pairs include sensor_11 / sensor_12, sensor_4 / sensor_11 and sensor_8 / sensor_13. Use ablation experiments rather than automatically dropping correlated features.

## 4. Initial modelling baseline plan

The first modelling experiment should remain deliberately comparable and interpretable.

### Candidate inputs

- Start with the 14 non-constant sensors other than near-constant sensor_6.
- Retain sensor_9 and sensor_14 initially, then run ablation experiments because they are strongly correlated and have inconsistent per-engine trend directions.
- Run a separate experiment adding sensor_6.
- Keep setting_1 and setting_2 available as contextual inputs for a comparison; setting_3 is constant in FD001.
- Keep unit_id as an identifier only. Preserve cycle for sorting, grouping, target construction and traceability; evaluate cycle as an optional elapsed-age feature in a controlled ablation.

### Candidate features

Start with current-cycle sensor values. Compare against causal, per-engine features such as:
- rolling mean,
- rolling standard deviation,
- recent difference,
- recent trend/slope,
- deviation from an early per-engine baseline.

All rolling calculations must be grouped by engine, ordered by cycle and computed using current and past rows only.

### Validation

- Split training data by engine ID, never by individual rows.
- Keep every trajectory from one engine entirely within one split.
- Fit preprocessing and feature selection only on the training-engine subset.
- Keep the official test trajectories and their RUL labels isolated for final benchmark evaluation.
- Compare uncapped RUL targets with an explicitly documented capped-target experiment; the cap is not a property of the raw dataset.
- Report MAE, RMSE and the benchmark's asymmetric scoring function, with per-engine error analysis.

### Anomaly detection

No per-row ground-truth anomaly label is supplied in FD001. Treat anomaly detection as a separate unsupervised or rule/statistics experiment. Do not report classification accuracy without a defensible labelled evaluation set. A controlled synthetic-corruption evaluation can test detection behaviour, but it must be clearly labelled as synthetic.

## 5. Model and operational assumptions

- The first version is an offline benchmark workflow plus a software replay demonstration.
- Replay/simulated telemetry must be labelled as simulated; no physical fleet integration is claimed.
- RUL is an estimate, not a guarantee of failure time.
- Triage rules will be calibrated only after validation and documented as advisory decisions.
- Work-order creation must be idempotent, traceable and reviewable by a human.
- Model retraining must use eligible labelled data and pass a candidate evaluation gate before promotion.

## 6. Phase 1 deliverables in the repository

| Deliverable | Location |
|---|---|
| Dataset structural audit | `docs/audits/fd001-data-audit.md` |
| RUL derivation and examples | `docs/rul-targets-and-examples.md` |
| Sensor behaviour analysis | `docs/audits/fd001-sensor-behaviour-analysis.md` |
| Read-only structural audit script | `scripts/inspect_fd001.py` |
| Sensor analysis script | `scripts/analyze_fd001_sensors.py` |
| Sensor metrics | `reports/phase1/fd001_sensor_metrics.csv` |
| Life-stage means | `reports/phase1/fd001_lifecycle_deciles.csv` |
| Pairwise sensor correlations | `reports/phase1/fd001_sensor_correlations.csv` |
| Setting/sensor correlations | `reports/phase1/fd001_setting_sensor_correlations.csv` |

## 7. What is intentionally not decided yet

Phase 1 does not select a winning ML algorithm, an RUL cap, a final feature subset, a model threshold or an anomaly detector. Those choices require Phase 2 data preparation and Phase 3 validation experiments.

## 8. Exit decision

Phase 1's research exit criteria are satisfied: dataset structure and target definitions are understood, sensor behaviour has been quantified, leakage risks and model scope are documented, and the initial experiment plan is recorded.

**Next: Phase 2 — Reproducible Data Engineering for FD001.**
