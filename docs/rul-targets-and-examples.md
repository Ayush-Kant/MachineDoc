# Understanding Remaining Useful Life (RUL) in C-MAPSS FD001

**Project:** FleetGuard  
**Authoritative project files:** `Ayush-Kant/MachineDoc` on `main`  
**Files used:** `train_FD001.txt`, `test_FD001.txt`, `RUL_FD001.txt`

This document explains how the FD001 target is represented and how to derive row-level RUL correctly. The numerical examples below were calculated from the exact files in this repository.

---

## 1. What does RUL mean?

Remaining Useful Life (RUL) is the number of additional operating cycles an engine is expected to complete before it reaches the simulated failure point.

For this benchmark, a row records the engine at a particular operating cycle. RUL is measured **after that recorded cycle**.

For example, if an engine's failure endpoint is cycle 192:

- At cycle 191, one additional cycle remains before the endpoint.
- At cycle 192, the engine has reached the endpoint, so RUL is zero.

This explains why the training formula subtracts the current cycle from the final cycle; it does not add one.

## 2. Why training and test RUL are different

### Training trajectories

The training file contains full run-to-failure trajectories. We can see the final cycle for each training engine. That lets us calculate a target for every observed training row.

For engine (u), define:

- (C_{max,u}): the final cycle recorded for engine (u) in the training file.
- (c): the current row's cycle.

Then:

`RUL_{train}(u,c) = C_{max,u} - c`

The formula is applied separately to each engine. It is not correct to subtract a global maximum cycle across all engines.

### Test trajectories

The test file contains truncated trajectories. Their observed final cycle is **not** the failure cycle. We therefore cannot calculate test RUL by subtracting the current cycle from the maximum cycle in the test file.

Instead, `RUL_FD001.txt` contains one ground-truth RUL label for each test engine. Each value describes the number of additional cycles remaining **after that engine's final observed test cycle**.

For engine (u), define:

- (C_{last,u}): the final cycle observed for engine (u) in `test_FD001.txt`.
- (RUL_{final,u}): the corresponding value in `RUL_FD001.txt`.
- (c): a cycle in the observed test trajectory.

The row-level quantity can be derived as:

`RUL_{test}(u,c) = (C_{last,u} - c) + RUL_{final,u}`

The supplied RUL file is ordered by test engine number. In our files, test engine IDs are 1 through 100, there are 100 RUL values, and the ordering aligns one-to-one with ascending engine ID.

**For the benchmark's final test evaluation, the important prediction is the RUL at each engine's final observed test row.** At that row, (C_{last,u}-c=0), so the formula reduces exactly to the supplied RUL value.

---

## 3. Real example from training engine 1

From `train_FD001.txt`, engine 1 has 192 observations. Its cycles run from 1 through 192.

Therefore:

`C_{max,1} = 192`

| Current cycle | Calculation | Training RUL |
|---:|---:|---:|
| 1 | 192 - 1 | 191 |
| 96 | 192 - 96 | 96 |
| 191 | 192 - 191 | 1 |
| 192 | 192 - 192 | 0 |

Interpretation:

- At cycle 1, 191 further cycles are counted until the cycle-192 failure endpoint.
- At cycle 96, 96 further cycles remain.
- At cycle 191, one further cycle remains.
- At cycle 192, the trajectory reaches its run-to-failure endpoint.

The first, middle and final raw observations for engine 1 were checked in the repository file. The cycle values are 1, 96 and 192 for these examples.

## 4. Real example from test engine 1

From `test_FD001.txt`, test engine 1 has 31 observed cycles (1 through 31).

The first value in `RUL_FD001.txt` is 112. Since test engine IDs are 1–100 in ascending order, this is the final-observation RUL for test engine 1.

Thus:

`C_{last,1} = 31`

`RUL_{final,1} = 112`

| Current observed cycle | Calculation | Derived test RUL |
|---:|---:|---:|
| 1 | (31 - 1) + 112 | 142 |
| 16 | (31 - 16) + 112 | 127 |
| 30 | (31 - 30) + 112 | 113 |
| 31 | (31 - 31) + 112 | 112 |

The key point is that **cycle 31 is not the failure cycle**. It is merely the last cycle available in the test file. The supplied label says that another 112 cycles remain after it.

The model is evaluated on the last observed row for this engine against 112.

## 5. More examples calculated from the exact files

### Training examples

| Engine | Final training cycle | RUL at cycle 1 | RUL at final cycle |
|---:|---:|---:|---:|
| 1 | 192 | 191 | 0 |
| 2 | 287 | 286 | 0 |
| 3 | 179 | 178 | 0 |
| 10 | 222 | 221 | 0 |
| 50 | 198 | 197 | 0 |
| 100 | 200 | 199 | 0 |

### Test examples

| Engine | Last observed cycle | Supplied final RUL | Derived RUL at cycle 1 |
|---:|---:|---:|---:|
| 1 | 31 | 112 | 142 |
| 2 | 49 | 98 | 146 |
| 3 | 126 | 69 | 194 |
| 10 | 192 | 96 | 287 |
| 50 | 74 | 79 | 152 |
| 100 | 198 | 20 | 217 |

The final RUL labels for test engines 1–10 begin:

`112, 98, 69, 82, 91, 93, 91, 95, 111, 96`

The complete file contains 100 labels:

- Minimum: 7 cycles
- 25th percentile: 32.75 cycles
- Median: 86 cycles
- Mean: 75.52 cycles
- 75th percentile: 112.25 cycles
- Maximum: 145 cycles

These statistics describe the **100 final-observation labels**, not all 13,096 test rows.

---

## 6. Visualize the two timelines

### Training engine

`Cycle 1 ─────── Cycle 96 ─────── Cycle 191 ── Cycle 192`

`RUL 191             96              1              0`

The failure endpoint is visible in the training trajectory.

### Test engine 1

`Cycle 1 ─────── Cycle 16 ─────── Cycle 30 ── Cycle 31 ───── 112 future cycles ───── Failure endpoint`

`RUL 142            127             113           112`

The test trajectory ends before the failure endpoint. The RUL file provides the missing distance from the final observed cycle to the endpoint.

---

## 7. Common mistakes to avoid

1. **Using the global maximum cycle:** Every engine has its own final training cycle. Calculate the endpoint per engine.
2. **Treating the test file's last cycle as failure:** Test trajectories are truncated, not run to failure.
3. **Assuming the RUL file has one label per test row:** It contains one label per test engine, 100 values for FD001.
4. **Pairing labels with the wrong engine:** Preserve the documented order. Here, engine IDs are 1–100 and the RUL vector has 100 entries.
5. **Adding one to the training formula:** RUL counts additional cycles after the current recorded cycle; at the terminal training cycle the target is zero.
6. **Using test RUL as a model input:** The RUL file is ground truth for evaluation. It must never enter the feature matrix.
7. **Confusing row-level derived test targets with official endpoint evaluation:** Earlier test-row labels can be derived for analysis, but the supplied benchmark label refers to the final observed row.
8. **Using future readings to predict an earlier cycle:** A prediction at cycle (c) must only use information available at or before cycle (c).

---

## 8. RUL capping: a later modelling decision, not a raw-data fact

Some RUL modelling approaches cap large target values at a chosen threshold to represent an early-life period where the engine is treated as broadly healthy. The original FD001 files do not contain such a cap.

We will not silently impose one. In Phase 2/3, we will compare:
- An uncapped target using the formulas above.
- A capped target as a separately documented modelling experiment, with the cap selected and justified.

The raw derived target and the modelling target must remain distinguishable.

---

## 9. Minimal Python demonstration

This snippet shows the correct grouping and formulas after loading the files as data frames with the 26 named columns.

```python
# Training: calculate the failure endpoint separately for every engine.
train_last_cycle = train.groupby("unit_id")["cycle"].transform("max")
train["RUL"] = train_last_cycle - train["cycle"]

# Test: the RUL file gives the remaining cycles after each engine's
# final observed row. The file order corresponds to ascending test unit ID.
test_units = sorted(test["unit_id"].unique())
rul_by_unit = dict(zip(test_units, rul_values))

test_last_cycle = test.groupby("unit_id")["cycle"].transform("max")
test_final_rul = test["unit_id"].map(rul_by_unit)

test["RUL"] = (
    test_last_cycle - test["cycle"] + test_final_rul
)
```

Do not add the test `RUL` column to inference features. It is a target for evaluation and analysis only.

---

## 10. Phase 1 conclusions

We now understand the benchmark's target construction:

- Training data: derive row-level RUL from each engine's run-to-failure endpoint.
- Test data: use the supplied per-engine endpoint RUL, and add the distance from an earlier observed cycle to the last observed cycle only when row-level analysis is needed.
- Final benchmark evaluation: compare the prediction at each test engine's last observed row against its supplied RUL value.
- Data integrity: keep engine identity, cycle ordering and test RUL alignment intact throughout the pipeline.

**Next Phase 1 topic:** inspect sensor behaviour over time and determine which columns carry useful degradation information. No model or feature selection decision is made in this document.
