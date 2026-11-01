# NASA C-MAPSS Dataset Guide

## 1. Source

Use the original C-MAPSS archive downloaded from the NASA Prognostics Center of Excellence / NASA Open Data catalogue. Keep an unchanged local copy. Do not commit the raw archive or extracted files to Git.

- NASA PCoE repository: https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/
- NASA Open Data catalogue: https://catalog.data.gov/dataset/cmapss-jet-engine-simulated-data
- Reference paper: Saxena et al., “Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation,” PHM 2008, https://doi.org/10.1109/PHM.2008.4711414

## 2. Expected archive contents

The screenshot provided during project setup shows the following files inside `CMAPSSData`:

- `readme`
- `Damage Propagation Modeling` (PDF)
- `train_FD001.txt` through `train_FD004.txt`
- `test_FD001.txt` through `test_FD004.txt`
- `RUL_FD001.txt` through `RUL_FD004.txt`

This is a visual confirmation of the filenames, not yet a programmatic validation of their contents. The next inspection step must read the archive readme and load FD001 with a whitespace-delimited parser.

## 3. Original row schema

Each raw row contains 26 numeric fields, in this order:

1. Unit / engine identifier
2. Operating cycle
3. Operational setting 1
4. Operational setting 2
5. Operational setting 3
6–26. Sensor measurements 1–21

Use neutral source-aligned names initially:
`unit_id`, `cycle`, `setting_1`, `setting_2`, `setting_3`, `sensor_1` ... `sensor_21`.

Do not assign engineering meanings or units to generic sensor numbers unless the source documentation explicitly maps them.

## 4. Train / test distinction

- Training trajectories are run to failure; their final observed cycle is the failure cycle in the simulated trajectory.
- Test trajectories stop before failure.
- The corresponding `RUL_FDxxx.txt` file provides the true number of additional cycles after the last observed test cycle for each test engine, in the order of test engine IDs.

Preserve the official test RUL vector and verify that its number of rows equals the number of distinct test engines.

## 5. RUL target definitions

For a training engine (u), let (C_{max,u}) be its final training cycle. For an observed cycle (c):

`RUL(u,c) = C_max,u - c`

For a test engine, let (C_{last,u}) be its last observed cycle and let (RUL_{final,u}) be its value in the supplied RUL file:

`RUL(u,c) = C_last,u - c + RUL_final,u`

The supplied test RUL is for the engine's final observed row. Earlier per-row test RUL values can be derived using the formula above for analysis, but the benchmark's official endpoint evaluation uses each engine's final observed row.

## 6. Important modelling safeguards

- Do not use test RUL values as input features.
- Do not fit scalers, imputers or feature selectors using test data.
- Keep all rows from an engine together when creating a validation split.
- Do not shuffle time steps within an engine.
- Do not treat each row as an independent machine.
- Avoid assuming every sensor is informative; profile constant and near-constant sensors.
- Document any RUL clipping/capping as a modelling choice and compare it with an uncapped baseline.
- Keep original identifiers and cycle values available for traceability.

## 7. First inspection checklist

- [ ] Open the archive readme and record the stated column order.
- [ ] Load `train_FD001.txt`, `test_FD001.txt` and `RUL_FD001.txt`.
- [ ] Assert 26 columns for both trajectory matrices.
- [ ] Confirm finite numeric values and inspect whitespace parsing.
- [ ] Count distinct units and rows.
- [ ] Verify each unit's cycle sequence is ordered and unique.
- [ ] Check training trajectory terminal cycles.
- [ ] Check one-to-one alignment between test units and RUL vector.
- [ ] Inspect sensor distributions, constant columns and time trends.
- [ ] Record data-validation results before feature engineering.


## 8. Detailed RUL explanation

See [Understanding Remaining Useful Life (RUL) in C-MAPSS FD001](rul-targets-and-examples.md) for:
- training RUL derivation with exact engine examples,
- test endpoint RUL alignment and row-level reconstruction,
- common target-generation errors,
- leakage precautions and capped-vs-uncapped target considerations.
