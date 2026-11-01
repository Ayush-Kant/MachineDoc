# FD001 Dataset Structural Audit

**Project:** FleetGuard  
**Repository:** Ayush-Kant/MachineDoc  
**Branch:** main  
**Audit scope:** Read-only structural and target-alignment inspection of the FD001 train, test and RUL files fetched from this repository.

## 1. Source files inspected

| File | Git blob SHA | Characters retrieved | Non-blank lines |
|---|---|---:|---:|
| train_FD001.txt | `d2809918c8b75fa3319714658ae994deb2017a89` | 3,515,356 | 20,631 |
| test_FD001.txt | `7844fbf8d6ad32176f92544ad4f4c456481d930d` | 2,228,855 | 13,096 |
| RUL_FD001.txt | `e8dd7cfeee96d2dfd55166f5758227d36c096dd3` | 429 | 100 |

The repository tree confirms all three files are present on `main`. The blob identifiers above identify the exact versions inspected.

## 2. Structural validation results

| Check | Training | Testing |
|---|---:|---:|
| Rows | 20,631 | 13,096 |
| Columns | 26 | 26 |
| Distinct engines | 100 | 100 |
| Engine ID range | 1–100 | 1–100 |
| All engine IDs consecutive from 1 | Pass | Pass |
| Malformed/non-numeric rows | 0 | 0 |
| Missing or non-finite values | 0 | 0 |
| Exact duplicate rows | 0 | 0 |
| Per-engine cycles ordered and consecutive from 1 | Pass | Pass |

### Trajectory lengths

| Statistic | Training | Testing |
|---|---:|---:|
| Minimum | 128 | 31 |
| 25th percentile | 177 | 88.75 |
| Median | 199 | 133.5 |
| Mean | 206.31 | 130.96 |
| 75th percentile | 229.25 | 164.25 |
| Maximum | 362 | 303 |

Training trajectories are longer on average because the training subset runs to the simulated failure point. Test trajectories stop earlier.

## 3. Column findings

Each trajectory row contains:

- Column 1: engine identifier (`unit_id`)
- Column 2: operating cycle (`cycle`)
- Columns 3–5: three operational settings
- Columns 6–26: 21 sensor measurements (`sensor_1` through `sensor_21`)

Seven training columns are constant throughout FD001:

| Column | Constant value |
|---|---:|
| setting_3 | 100 |
| sensor_1 | 518.67 |
| sensor_5 | 14.62 |
| sensor_10 | 1.30 |
| sensor_16 | 0.03 |
| sensor_18 | 2388 |
| sensor_19 | 100 |

Thus, 15 of 21 sensor columns vary in the training subset. `sensor_6` is not exactly constant; it has two distinct values (21.60 and 21.61) in the training file. Constant and near-constant features will be handled through an explicit, training-only feature-selection decision rather than automatically dropped without evaluation.

## 4. RUL file validation

| Check | Result |
|---|---:|
| Values | 100 |
| Integer and non-negative | Pass |
| One value per test engine | Pass |
| Minimum | 7 cycles |
| 25th percentile | 32.75 cycles |
| Median | 86 cycles |
| Mean | 75.52 cycles |
| 75th percentile | 112.25 cycles |
| Maximum | 145 cycles |

The test engine IDs are 1–100. The RUL vector contains 100 values and aligns one-to-one with the test engines in ascending engine-ID order. Reconstructing the RUL at every engine's final observed test cycle reproduces the supplied RUL value.

## 5. Target construction

### Training target

For engine (u), define its final training cycle as (C_{max,u}). The row-level target at cycle (c) is:

`RUL(u,c) = C_{max,u} - c`

The 20,631 derived training targets range from 0 to 361 cycles, with mean 107.808 cycles and median 103 cycles.

### Test target

The supplied test RUL value is for each engine's final observed cycle. Let that final observed cycle be (C_{last,u}), and the supplied endpoint label be (RUL_{final,u}). For an earlier observed row:

`RUL(u,c) = C_{last,u} - c + RUL_{final,u}`

The derived row-level test target ranges from 7 to 340 cycles. The final-row reconstruction matches all 100 supplied labels.

**Leakage warning:** The supplied test RUL file is a benchmark ground-truth target for final evaluation. It must never be included among model input features. Validation splitting and preprocessing must be designed to prevent engine/time leakage.

## 6. Decisions for the next phase

1. Keep the original train, test and RUL files immutable.
2. Use engine-aware splits for validation; never randomly split rows from the same engine across train and validation.
3. Fit scalers, imputers and feature selectors only on training data.
4. Compare capped and uncapped RUL target formulations rather than assuming one.
5. Keep anomaly scores distinct from RUL estimates; the dataset does not provide row-level anomaly labels.
6. Preserve `unit_id` and `cycle` for traceability, but do not feed the engine ID as an ordinary sensor feature.
7. Evaluate the official test endpoint predictions separately from row-level training diagnostics.

## 7. Reproducibility

A read-only audit script is available at [`scripts/inspect_fd001.py`](../../scripts/inspect_fd001.py). Run it from the repository root:

```bash
python -m pip install pandas numpy
python scripts/inspect_fd001.py
```

The default data-directory detection checks the repository root and planned local data directories. The script writes a JSON report under `reports/phase1/fd001_audit.json` and does not alter the raw files.

**Audit boundary:** The numerical findings above were calculated from the remote Git blob contents fetched from `Ayush-Kant/MachineDoc`. The committed Python script is provided for independent local reproduction; it has not been run on the user's unavailable local computer.
