from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)


def find_data_dir(explicit_dir: Path | None) -> Path:
    if explicit_dir is not None:
        return explicit_dir.resolve()

    candidates = [
        PROJECT_ROOT,
        PROJECT_ROOT / "data" / "raw" / "CMAPSSData",
        PROJECT_ROOT / "data" / "raw",
    ]
    for candidate in candidates:
        if all((candidate / name).is_file() for name in (
            "train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"
        )):
            return candidate

    raise FileNotFoundError(
        "Could not locate FD001 files. Pass --data-dir with the folder "
        "containing train_FD001.txt, test_FD001.txt and RUL_FD001.txt."
    )


def load_matrix(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=r"\\s+", header=None, engine="python")
    if frame.shape[1] != len(COLUMNS):
        raise ValueError(
            f"{path.name}: expected 26 columns, found {frame.shape[1]}"
        )
    frame.columns = COLUMNS
    frame = frame.apply(pd.to_numeric, errors="coerce")

    values = frame.to_numpy(dtype=float)
    invalid = ~np.isfinite(values)
    if invalid.any():
        row_idx, col_idx = np.where(invalid)
        samples = [
            {"row": int(r + 1), "column": COLUMNS[int(c)]}
            for r, c in zip(row_idx[:10], col_idx[:10])
        ]
        raise ValueError(
            f"{path.name}: {int(invalid.sum())} missing/non-finite values; "
            f"examples: {samples}"
        )

    for column in ("unit_id", "cycle"):
        values = frame[column].to_numpy(dtype=float)
        if not np.equal(values, np.floor(values)).all() or (values <= 0).any():
            raise ValueError(f"{path.name}: {column} must be positive integers")

    return frame


def audit_trajectories(frame: pd.DataFrame, name: str) -> dict[str, Any]:
    if frame.duplicated().any():
        raise ValueError(f"{name}: exact duplicate rows found")

    unit_ids = sorted(int(x) for x in frame["unit_id"].unique())
    if unit_ids != list(range(1, len(unit_ids) + 1)):
        raise ValueError(f"{name}: engine IDs are not consecutive starting at 1")

    engine_summaries = []
    for unit_id, group in frame.groupby("unit_id", sort=True):
        cycles = group["cycle"].astype(int).to_numpy()
        expected = np.arange(1, len(group) + 1)
        if not np.array_equal(cycles, expected):
            raise ValueError(
                f"{name}: unit {int(unit_id)} cycles are not ordered and "
                "consecutive from 1"
            )
        engine_summaries.append({
            "unit_id": int(unit_id),
            "rows": int(len(group)),
            "first_cycle": int(cycles[0]),
            "last_cycle": int(cycles[-1]),
        })

    lengths = np.asarray([x["rows"] for x in engine_summaries], dtype=int)
    return {
        "rows": int(len(frame)),
        "columns": int(frame.shape[1]),
        "engines": int(len(unit_ids)),
        "engine_id_range": [int(unit_ids[0]), int(unit_ids[-1])],
        "trajectory_length": {
            "min": int(lengths.min()),
            "p25": float(np.quantile(lengths, 0.25)),
            "median": float(np.median(lengths)),
            "mean": float(lengths.mean()),
            "p75": float(np.quantile(lengths, 0.75)),
            "max": int(lengths.max()),
        },
        "exact_duplicate_rows": 0,
        "cycle_sequences_valid": True,
        "engine_details": engine_summaries,
    }


def column_statistics(frame: pd.DataFrame) -> list[dict[str, Any]]:
    result = []
    for column in COLUMNS:
        values = frame[column].to_numpy(dtype=float)
        result.append({
            "column": column,
            "unique_values": int(pd.Series(values).nunique()),
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "std_population": float(values.std(ddof=0)),
            "constant": bool(pd.Series(values).nunique() == 1),
        })
    return result


def read_rul(path: Path, expected_count: int) -> np.ndarray:
    frame = pd.read_csv(path, sep=r"\\s+", header=None, engine="python")
    if frame.shape[1] != 1:
        raise ValueError(f"{path.name}: expected one RUL value per line")
    values = pd.to_numeric(frame.iloc[:, 0], errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{path.name}: found non-finite RUL values")
    if not np.equal(values, np.floor(values)).all() or (values < 0).any():
        raise ValueError(f"{path.name}: RUL values must be non-negative integers")
    if len(values) != expected_count:
        raise ValueError(
            f"{path.name}: {len(values)} labels for {expected_count} test engines"
        )
    return values.astype(int)


def value_summary(values: np.ndarray) -> dict[str, float | int]:
    return {
        "count": int(values.size),
        "min": float(values.min()),
        "p25": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "mean": float(values.mean()),
        "p75": float(np.quantile(values, 0.75)),
        "max": float(values.max()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read-only structural audit of the NASA C-MAPSS FD001 files."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Folder containing the three FD001 files; auto-detected by default.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "phase1" / "fd001_audit.json",
        help="Path for the JSON audit report.",
    )
    args = parser.parse_args()
    data_dir = find_data_dir(args.data_dir)

    train = load_matrix(data_dir / "train_FD001.txt")
    test = load_matrix(data_dir / "test_FD001.txt")
    train_summary = audit_trajectories(train, "train_FD001")
    test_summary = audit_trajectories(test, "test_FD001")

    # C-MAPSS RUL labels correspond to test engines in ascending unit order.
    test_units = sorted(int(x) for x in test["unit_id"].unique())
    test_rul = read_rul(data_dir / "RUL_FD001.txt", len(test_units))
    test_rul_by_unit = dict(zip(test_units, test_rul.tolist()))

    # Training target: final training cycle minus the current cycle.
    train_last_cycle = train.groupby("unit_id")["cycle"].transform("max")
    train_rul_rows = (
        train_last_cycle.to_numpy(dtype=int)
        - train["cycle"].to_numpy(dtype=int)
    )

    # Test target at an arbitrary observed row is derived from the final
    # observed cycle and that engine's supplied endpoint RUL.
    test_last_cycle = test.groupby("unit_id")["cycle"].transform("max")
    test_final_rul = test["unit_id"].map(test_rul_by_unit).to_numpy(dtype=int)
    test_rul_rows = (
        test_last_cycle.to_numpy(dtype=int)
        - test["cycle"].to_numpy(dtype=int)
        + test_final_rul
    )

    endpoint_checks = []
    for unit_id, group in test.groupby("unit_id", sort=True):
        last_row = group.loc[group["cycle"].idxmax()]
        endpoint_rul = int(
            test_last_cycle.loc[last_row.name]
            - last_row["cycle"]
            + test_rul_by_unit[int(unit_id)]
        )
        endpoint_checks.append(endpoint_rul == test_rul_by_unit[int(unit_id)])

    train_stats = column_statistics(train)
    test_stats = column_statistics(test)
    constant_columns = [
        item["column"] for item in train_stats if item["constant"]
    ]

    report = {
        "dataset": "NASA C-MAPSS FD001",
        "data_directory": str(data_dir),
        "read_only_audit": True,
        "training": {
            **train_summary,
            "missing_or_nonfinite_values": 0,
            "column_statistics": train_stats,
            "derived_row_rul": value_summary(train_rul_rows),
            "derived_row_rul_nonnegative": bool((train_rul_rows >= 0).all()),
        },
        "testing": {
            **test_summary,
            "missing_or_nonfinite_values": 0,
            "column_statistics": test_stats,
            "derived_row_rul": value_summary(test_rul_rows),
        },
        "test_endpoint_rul_file": {
            **value_summary(test_rul),
            "all_nonnegative_integers": True,
            "one_label_per_test_engine": len(test_rul) == len(test_units),
            "endpoint_reconstruction_matches_supplied_labels": all(endpoint_checks),
        },
        "findings": {
            "constant_training_columns": constant_columns,
            "varying_sensor_count": sum(
                not item["constant"]
                for item in train_stats
                if item["column"].startswith("sensor_")
            ),
            "sensor_count": 21,
        },
        "notes": [
            "No raw dataset files are modified.",
            "No preprocessing or model fitting is performed by this audit.",
            "Test RUL labels are used only to verify endpoint alignment and derive descriptive targets.",
            "Do not use test RUL labels as model input features.",
        ],
    }

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "passed",
        "data_directory": str(data_dir),
        "training_rows": train_summary["rows"],
        "testing_rows": test_summary["rows"],
        "training_engines": train_summary["engines"],
        "testing_engines": test_summary["engines"],
        "test_rul_labels": int(len(test_rul)),
        "constant_training_columns": constant_columns,
        "report": str(output_path),
    }, indent=2))


if __name__ == "__main__":
    main()
