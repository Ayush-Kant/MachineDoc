# FD001 Sensor Behaviour and Degradation Analysis

**Project:** FleetGuard  
**Dataset:** NASA C-MAPSS FD001  
**Repository source:** `Ayush-Kant/MachineDoc`, branch `main`  
**Analysis type:** Retrospective exploratory analysis of the 20,631 training rows and 100 complete training engine trajectories.

## 1. Exact source files

The analysis used the three exact files in this repository:

| File | Git blob SHA |
|---|---|
| `train_FD001.txt` | `d2809918c8b75fa3319714658ae994deb2017a89` |
| `test_FD001.txt` | `7844fbf8d6ad32176f92544ad4f4c456481d930d` |
| `RUL_FD001.txt` | `e8dd7cfeee96d2dfd55166f5758227d36c096dd3` |

The training file was used for degradation trend analysis because its trajectories run to the simulated failure endpoint. Test files were checked for continuity with the prior structural audit; their partial trajectories are not treated as complete lifecycles.

## 2. How this analysis was performed

The training rows were grouped by engine ID and sorted by cycle. For every sensor:

1. Basic distribution statistics were calculated over all training rows.
2. A Pearson correlation between cycle and sensor value was calculated separately for each engine. The report records the median and 10th/90th percentiles across engines.
3. A per-engine linear slope was calculated by ordinary least squares against cycle; the number of engines with positive and negative slopes was counted.
4. The mean of the first 10% of readings was compared with the mean of the last 10% for each engine.
5. Each engine's complete trajectory was divided retrospectively into ten normalized life-stage bins. A mean was calculated within each engine and bin, then engine means were averaged equally so longer trajectories do not dominate the fleet curve.
6. Pearson correlations between varying sensors were calculated across the pooled training rows.
7. Descriptive pooled-row correlations between each sensor and the derived row-level training RUL were calculated.

The normalized lifecycle analysis is descriptive only. It uses each engine's complete trajectory length, which would not be known for a live engine that has not failed. Normalized life stage must not be used as a prediction-time feature.

## 3. Main finding: several sensors have consistent degradation trends

The strongest result is not simply that fleet-average values change. It is that multiple sensors move in the same direction within every one of the 100 training engines.

### Sensors that increase consistently

| Sensor | Engines with positive linear slope | Median within-engine corr. with cycle | 10th–90th percentile |
|---|---:|---:|---:|
| sensor_2 | 100/100 | +0.683 | +0.602 to +0.746 |
| sensor_3 | 100/100 | +0.654 | +0.560 to +0.714 |
| sensor_4 | 100/100 | +0.790 | +0.731 to +0.822 |
| sensor_8 | 100/100 | +0.778 | +0.364 to +0.840 |
| sensor_11 | 100/100 | +0.816 | +0.756 to +0.852 |
| sensor_13 | 100/100 | +0.774 | +0.370 to +0.838 |
| sensor_15 | 100/100 | +0.735 | +0.647 to +0.784 |
| sensor_17 | 100/100 | +0.681 | +0.600 to +0.742 |

The first-to-last 10% mean also increased in all 100 engines for every sensor in this table.

### Sensors that decrease consistently

| Sensor | Engines with negative linear slope | Median within-engine corr. with cycle | 10th–90th percentile |
|---|---:|---:|---:|
| sensor_7 | 100/100 | -0.783 | -0.823 to -0.682 |
| sensor_12 | 100/100 | -0.811 | -0.838 to -0.714 |
| sensor_20 | 100/100 | -0.717 | -0.783 to -0.649 |
| sensor_21 | 100/100 | -0.730 | -0.779 to -0.651 |

The first-to-last 10% mean decreased in all 100 engines for each sensor in this table.

These sensors form a strong initial feature-candidate group. Consistent direction is useful evidence, but it does not prove that any sensor alone can predict RUL accurately.

## 4. Sensors with inconsistent or weak behaviour

### sensor_9

- 6,403 distinct values across the training rows.
- Median within-engine cycle correlation: +0.747.
- 10th percentile of within-engine correlation: -0.518.
- Positive linear slope in 71 engines; negative slope in 29.
- First/last 10% mean increased in 71 engines and decreased in 29.
- Fleet life-stage mean increased from approximately 9,056.00 in the first bin to 9,090.67 in the final bin.
- Between-engine standard deviation of per-engine life-stage means rose from about 7.33 in the first bin to 44.05 in the final bin.

The median trend is positive, but its direction is not consistent across engines. Late-life behaviour is also highly heterogeneous.

### sensor_14

- 6,078 distinct values.
- Median within-engine cycle correlation: +0.670.
- 10th percentile: -0.763.
- Positive linear slope in 60 engines; negative slope in 40.
- First/last 10% mean increased in 57 engines and decreased in 43.
- Between-engine standard deviation of life-stage means rose from about 7.27 to 40.00 from the first to final bin.

This sensor also shows a positive fleet-average life-stage trend but has substantial engine-to-engine variation and inconsistent per-engine direction.

### sensor_6

- Only two distinct values: 21.60 and 21.61.
- Positive linear slope in 61 engines, negative in one; 38 slopes are zero.
- First/last 10% mean increased in only 40 engines; it was unchanged in 60.
- Fleet-average life-stage correlation is about +0.981, but the total shift between first and last life-stage means is only about 0.00046, or 0.33 of its overall training standard deviation.

This is a useful warning: a high correlation can occur for a tiny, low-information change. Do not rank sensors by correlation alone.

## 5. Normalized lifecycle trends

The following table gives the equal-engine mean in the first and final normalized life-stage bins. The standardized span is the end-to-end change divided by the sensor's overall training standard deviation.

| Sensor | First 0–10% mean | Final 90–100% mean | Change in global SD |
|---|---:|---:|---:|
| sensor_2 | 642.38609 | 643.47844 | +2.18 |
| sensor_3 | 1586.83339 | 1600.00958 | +2.15 |
| sensor_4 | 1402.79381 | 1424.89378 | +2.46 |
| sensor_7 | 553.94943 | 551.84744 | -2.37 |
| sensor_8 | 2388.05832 | 2388.20360 | +2.05 |
| sensor_11 | 47.35323 | 48.02892 | +2.53 |
| sensor_12 | 521.91358 | 520.11973 | -2.43 |
| sensor_13 | 2388.05600 | 2388.20415 | +2.06 |
| sensor_15 | 8.41809 | 8.50581 | +2.34 |
| sensor_17 | 392.28748 | 395.67542 | +2.19 |
| sensor_20 | 38.93274 | 38.51999 | -2.28 |
| sensor_21 | 23.36019 | 23.11020 | -2.31 |

The lifecycle CSV contains all 21 sensors across all ten bins, including between-engine standard deviation and engine count.

### Interpretation

- Several signals show gradual movement across the whole observed life, with stronger changes in later bins.
- The direction is not identical across all sensors: some increase and some decrease.
- The mean curve summarizes the fleet; it does not mean every engine follows the exact same curve.
- Late-life dispersion rises sharply for sensors 9 and 14, unlike the more consistent signals above.

## 6. Constant and near-constant columns

The following six sensor columns are constant in FD001 training and therefore contain no variation to learn from in this subset:

- sensor_1
- sensor_5
- sensor_10
- sensor_16
- sensor_18
- sensor_19

They should not be useful as predictive inputs for FD001. Keeping their source columns in raw files is still important for reproducibility and schema compatibility.

The seventh constant column in the full 26-column file is setting_3, which is an operating setting rather than a sensor.

sensor_6 is not constant, but has only two unique values. Treat it as near-constant and test its inclusion/exclusion rather than assuming it adds useful signal.

## 7. Sensor-to-sensor correlation and redundancy

The strongest Pearson relationships between varying sensors in pooled training rows include:

| Sensor pair | Correlation |
|---|---:|
| sensor_9 / sensor_14 | +0.9632 |
| sensor_11 / sensor_12 | -0.8469 |
| sensor_4 / sensor_11 | +0.8301 |
| sensor_8 / sensor_13 | +0.8261 |
| sensor_7 / sensor_11 | -0.8228 |
| sensor_4 / sensor_12 | -0.8156 |
| sensor_7 / sensor_12 | +0.8127 |
| sensor_4 / sensor_7 | -0.7931 |
| sensor_12 / sensor_13 | -0.7884 |
| sensor_8 / sensor_12 | -0.7865 |

The sensor_9/sensor_14 pair is particularly highly correlated, but both have heterogeneous within-engine trends. For a linear model, this can create multicollinearity. For tree-based models, correlated inputs may still influence feature importance and split usage.

Do not automatically remove one member of every correlated pair. Compare all-sensor and reduced-feature baselines, and use engine-level validation to assess whether a sensor adds independent predictive value.

Constant columns are excluded from meaningful correlation ranking because Pearson correlation is undefined when a feature has zero variance.

## 8. Operating settings in FD001

| Setting | Unique values | Minimum | Maximum | Mean | Population SD |
|---|---:|---:|---:|---:|---:|
| setting_1 | 158 | -0.0087 | +0.0087 | -0.00000887 | 0.002187 |
| setting_2 | 13 | -0.0006 | +0.0006 | +0.00000235 | 0.000293 |
| setting_3 | 1 | 100 | 100 | 100 | 0 |

The strongest absolute pooled Pearson correlation between either varying setting (setting_1 or setting_2) and any sensor is approximately 0.0182.

This is descriptive linear correlation only. It does not rule out nonlinear or conditional effects. FD001 is documented as one operating condition; the small variation in setting_1 and setting_2 does not turn it into the six-condition FD002 problem. setting_3 is constant.

Keep setting_1 and setting_2 available as candidate covariates for the first model experiment. Exclude setting_3 from predictive features for FD001 due to zero variance.

## 9. Correlation with row-level RUL: useful but not a final ranking

Pooled Pearson correlations across all training rows were:

| Sensor | Pooled Pearson correlation with row-level RUL |
|---|---:|
| sensor_2 | -0.606 |
| sensor_3 | -0.585 |
| sensor_4 | -0.679 |
| sensor_6 | -0.128 |
| sensor_7 | +0.657 |
| sensor_8 | -0.564 |
| sensor_9 | -0.390 |
| sensor_11 | -0.696 |
| sensor_12 | +0.672 |
| sensor_13 | -0.563 |
| sensor_14 | -0.307 |
| sensor_15 | -0.643 |
| sensor_17 | -0.606 |
| sensor_20 | +0.629 |
| sensor_21 | +0.636 |

Interpretation: positive sensor-cycle trends generally have negative pooled correlation with RUL because RUL decreases as cycle increases. Decreasing sensors show the opposite sign.

These pooled correlations are not independent-observation statistics: many rows belong to the same engines, and each engine's target is constructed from its terminal cycle. Use them only for exploration, not final feature ranking. Final modelling decisions must use an engine-aware validation split and the benchmark's held-out test procedure.

## 10. Initial feature strategy for Phase 2 / Phase 3

This is an experiment plan, not a finalized feature selection.

### Candidate baseline sensor set

Start with the 14 varying sensors other than sensor_6:

- Increasing: sensor_2, sensor_3, sensor_4, sensor_8, sensor_9, sensor_11, sensor_13, sensor_14, sensor_15, sensor_17.
- Decreasing: sensor_7, sensor_12, sensor_20, sensor_21.

Although sensors 9 and 14 are inconsistent across engines, retain them in the initial wide baseline so validation can quantify whether their heterogeneity contains useful information.

### Ablation experiments

1. All 14 candidate sensors.
2. Remove sensor_9 or sensor_14 individually, then both, to measure redundancy.
3. Remove sensor_8 or sensor_13 individually to test their overlap.
4. Add sensor_6 and compare against the baseline.
5. Add setting_1 and setting_2 as candidate context variables.
6. Compare raw values with per-engine causal features (for example, rolling mean, rolling standard deviation, recent change and deviation from an early per-engine baseline).

### Constant columns

Do not use sensor_1, sensor_5, sensor_10, sensor_16, sensor_18, sensor_19 or setting_3 as FD001 predictive features because they have no observed variation in training.

### Leakage-safe feature rules

- Preserve unit_id and cycle as identifiers.
- Do not feed unit_id as a general sensor measurement.
- Do not use complete trajectory length, terminal cycle or normalized total-life percentage as a prediction-time feature.
- Rolling features must be computed within each engine, sorted by cycle, and must not cross engine boundaries.
- At cycle (c), only readings from cycle (c) and earlier may contribute.
- Fit transforms and feature selection on the training-engine split only.
- Keep test RUL labels separate from model input features.

## 11. Limits of this analysis

- Findings apply to FD001 only: one documented operating condition and one fault mode.
- Sensor identifiers are retained as generic sensor_1 through sensor_21. The dataset description supplied here does not provide engineering names or units for each sensor; this report does not invent them.
- A consistent trend is not proof of causation or a guarantee of prediction accuracy.
- Pearson correlation captures linear association and can miss nonlinear relationships.
- Pooled correlations can be influenced by engine-level differences and repeated observations.
- Normalized life-stage curves use the complete run-to-failure training trajectories; they are retrospective visual summaries, not live prediction features.
- No row-level ground-truth anomaly label is supplied in the FD001 files. This analysis does not claim supervised anomaly-detection accuracy.
- No model has been trained or evaluated in this phase.

## 12. Reproducible outputs

- [Sensor metrics CSV](../../reports/phase1/fd001_sensor_metrics.csv)
- [Normalized lifecycle deciles CSV](../../reports/phase1/fd001_lifecycle_deciles.csv)
- [Sensor correlation pairs CSV](../../reports/phase1/fd001_sensor_correlations.csv)
- [Operating-setting/sensor correlations CSV](../../reports/phase1/fd001_setting_sensor_correlations.csv)
- [Python analysis script](../../scripts/analyze_fd001_sensors.py)
- [Earlier structural audit](fd001-data-audit.md)
- [RUL derivation and examples](../rul-targets-and-examples.md)

Run the local analysis after installing the project's Python requirements:

```bash
python scripts/analyze_fd001_sensors.py
```

The script reads the three FD001 files locally, writes the four CSV outputs and generates lifecycle trend and sensor-correlation figures under `reports/phase1/figures`.

**Execution note:** The numerical results in this report were computed directly from the exact Git blob contents of the three files in `Ayush-Kant/MachineDoc` on `main`. The Python script has been committed for local reproduction; it has not been executed on the user's unavailable local computer.
