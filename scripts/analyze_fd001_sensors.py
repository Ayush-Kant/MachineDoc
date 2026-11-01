from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)
SENSORS = [f"sensor_{i}" for i in range(1, 22)]


def locate_data(data_dir: Path | None) -> Path:
    if data_dir is not None:
        return data_dir.resolve()
    candidates = [
        ROOT,
        ROOT / "data" / "raw" / "CMAPSSData",
        ROOT / "data" / "raw",
    ]
    for path in candidates:
        if all((path / name).is_file() for name in (
            "train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"
        )):
            return path
    raise FileNotFoundError(
        "FD001 files not found. Pass --data-dir pointing to their directory."
    )


def load_matrix(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    if frame.shape[1] != 26:
        raise ValueError(f"{path.name}: expected 26 columns; got {frame.shape[1]}")
    frame.columns = COLUMNS
    frame = frame.apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError(f"{path.name}: missing or non-finite values found")
    return frame


def pearson(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> float:
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def analyze(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = train.sort_values(["unit_id", "cycle"]).copy()
    train["RUL"] = (
        train.groupby("unit_id")["cycle"].transform("max") - train["cycle"]
    )

    engine_stats: dict[str, list[float]] = {
        sensor: [] for sensor in SENSORS
    }
    slope_stats: dict[str, list[float]] = {sensor: [] for sensor in SENSORS}
    delta_stats: dict[str, list[float]] = {sensor: [] for sensor in SENSORS}
    life_bins: dict[str, list[list[float]]] = {
        sensor: [[] for _ in range(10)] for sensor in SENSORS
    }

    for _, group in train.groupby("unit_id", sort=True):
        group = group.sort_values("cycle")
        cycles = group["cycle"].to_numpy(dtype=float)
        n = len(group)
        window = max(1, int(np.ceil(n * 0.10)))

        for sensor in SENSORS:
            values = group[sensor].to_numpy(dtype=float)
            c = pearson(cycles, values)
            if np.isfinite(c):
                engine_stats[sensor].append(c)

            centered_cycles = cycles - cycles.mean()
            centered_values = values - values.mean()
            denominator = np.square(centered_cycles).sum()
            slope = (
                float(np.dot(centered_cycles, centered_values) / denominator)
                if denominator else 0.0
            )
            slope_stats[sensor].append(slope)

            delta = float(values[-window:].mean() - values[:window].mean())
            delta_stats[sensor].append(delta)

            # Retrospective life-stage bins are for descriptive analysis only.
            # They use the complete trajectory length and must not be inference features.
            positions = np.linspace(0.0, 1.0, num=n)
            bin_ids = np.minimum(9, np.floor(positions * 10).astype(int))
            for bin_id in range(10):
                selected = values[bin_ids == bin_id]
                if selected.size:
                    life_bins[sensor][bin_id].append(float(selected.mean()))

    metric_rows = []
    decile_rows = []
    for sensor in SENSORS:
        values = train[sensor].to_numpy(dtype=float)
        stage_means = np.asarray([
            np.mean(per_engine_means) for per_engine_means in life_bins[sensor]
        ])
        stage_corr = pearson(np.arange(10, dtype=float), stage_means)
        within = np.asarray(engine_stats[sensor], dtype=float)
        slopes = np.asarray(slope_stats[sensor], dtype=float)
        deltas = np.asarray(delta_stats[sensor], dtype=float)
        sensor_std = float(values.std(ddof=0))

        metric_rows.append({
            "sensor": sensor,
            "unique_values": int(train[sensor].nunique()),
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "std_population": sensor_std,
            "constant": bool(train[sensor].nunique() == 1),
            "pooled_pearson_with_row_rul": pearson(values, train["RUL"]),
            "median_within_engine_pearson_cycle": float(np.median(within)) if within.size else np.nan,
            "p10_within_engine_pearson_cycle": float(np.quantile(within, 0.10)) if within.size else np.nan,
            "p90_within_engine_pearson_cycle": float(np.quantile(within, 0.90)) if within.size else np.nan,
            "engines_positive_slope": int((slopes > 0).sum()),
            "engines_negative_slope": int((slopes < 0).sum()),
            "median_slope_per_cycle": float(np.median(slopes)),
            "engines_positive_first_last_10pct_delta": int((deltas > 0).sum()),
            "engines_negative_first_last_10pct_delta": int((deltas < 0).sum()),
            "median_first_last_10pct_delta": float(np.median(deltas)),
            "life_stage_pearson": stage_corr,
            "life_stage_span_global_sd": (
                float((stage_means[-1] - stage_means[0]) / sensor_std)
                if sensor_std else np.nan
            ),
        })

        for bin_id, per_engine_means in enumerate(life_bins[sensor]):
            decile_rows.append({
                "sensor": sensor,
                "life_stage": f"{bin_id * 10}-{(bin_id + 1) * 10}%",
                "equal_engine_mean": float(np.mean(per_engine_means)),
                "between_engine_sd": float(np.std(per_engine_means, ddof=0)),
                "engines_in_stage": int(len(per_engine_means)),
            })

    sensor_corr = train[SENSORS].corr(method="pearson")
    corr_rows = []
    for i, sensor_a in enumerate(SENSORS):
        for sensor_b in SENSORS[i + 1:]:
            value = float(sensor_corr.loc[sensor_a, sensor_b])
            corr_rows.append({
                "sensor_a": sensor_a,
                "sensor_b": sensor_b,
                "pearson_correlation": value,
                "absolute_correlation": abs(value),
            })
    corr_rows.sort(key=lambda row: row["absolute_correlation"], reverse=True)

    setting_rows = []
    for setting in ["setting_1", "setting_2"]:
        for sensor in SENSORS:
            setting_rows.append({
                "setting": setting,
                "sensor": sensor,
                "pearson_correlation": pearson(train[setting], train[sensor]),
            })

    return (
        pd.DataFrame(metric_rows),
        pd.DataFrame(decile_rows),
        pd.DataFrame(corr_rows),
        pd.DataFrame(setting_rows),
    )


def make_plots(metrics: pd.DataFrame, deciles: pd.DataFrame, correlations: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    increasing = ["sensor_2", "sensor_3", "sensor_4", "sensor_8", "sensor_11", "sensor_13", "sensor_15", "sensor_17"]
    decreasing = ["sensor_7", "sensor_12", "sensor_20", "sensor_21"]

    metric_index = metrics.set_index("sensor")
    for title, sensors, filename in [
        ("Sensors increasing over normalized training life", increasing, "increasing_sensor_trends.png"),
        ("Sensors decreasing over normalized training life", decreasing, "decreasing_sensor_trends.png"),
    ]:
        fig, ax = plt.subplots(figsize=(12, 7))
        for sensor in sensors:
            values = deciles.loc[deciles["sensor"] == sensor, "equal_engine_mean"].to_numpy(dtype=float)
            base_std = float(metric_index.loc[sensor, "std_population"])
            z = (values - values[0]) / base_std if base_std else np.zeros_like(values)
            ax.plot(np.arange(10), z, marker="o", label=sensor)
        ax.set_xticks(np.arange(10), [f"{i * 10}-{(i + 1) * 10}%" for i in range(10)])
        ax.set_xlabel("Normalized position within each complete training trajectory")
        ax.set_ylabel("Change from first life-stage mean (global sensor standard deviations)")
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
        ax.legend(ncol=2)
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=160)
        plt.close(fig)

    pivot = correlations.pivot(index="sensor_a", columns="sensor_b", values="pearson_correlation")
    full = pd.DataFrame(np.eye(len(SENSORS)), index=SENSORS, columns=SENSORS)
    for a in SENSORS:
        for b in SENSORS:
            if a == b:
                continue
            if b in pivot.columns and a in pivot.index:
                value = pivot.loc[a, b]
            elif a in pivot.columns and b in pivot.index:
                value = pivot.loc[b, a]
            else:
                pair = correlations[
                    ((correlations["sensor_a"] == a) & (correlations["sensor_b"] == b))
                    | ((correlations["sensor_a"] == b) & (correlations["sensor_b"] == a))
                ]
                value = float(pair.iloc[0]["pearson_correlation"])
            full.loc[a, b] = value

    fig, ax = plt.subplots(figsize=(12, 10))
    image = ax.imshow(full.to_numpy(dtype=float), vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(np.arange(len(SENSORS)), SENSORS, rotation=90)
    ax.set_yticks(np.arange(len(SENSORS)), SENSORS)
    ax.set_title("FD001 training sensor Pearson correlation matrix")
    fig.colorbar(image, ax=ax, label="Pearson correlation")
    fig.tight_layout()
    fig.savefig(out_dir / "sensor_correlation_heatmap.png", dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep exploratory sensor analysis for FD001 training trajectories.")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports" / "phase1")
    args = parser.parse_args()

    data_dir = locate_data(args.data_dir)
    train = load_matrix(data_dir / "train_FD001.txt")
    # Load the test set as a schema/quality check. It is not used to create training trends.
    test = load_matrix(data_dir / "test_FD001.txt")
    test_rul = pd.read_csv(data_dir / "RUL_FD001.txt", sep=r"\s+", header=None).iloc[:, 0]
    if len(test_rul) != test["unit_id"].nunique():
        raise ValueError("RUL file row count does not match the number of test engines.")

    metrics, deciles, correlations, setting_correlations = analyze(train)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "fd001_sensor_metrics.csv", index=False)
    deciles.to_csv(args.output_dir / "fd001_lifecycle_deciles.csv", index=False)
    correlations.to_csv(args.output_dir / "fd001_sensor_correlations.csv", index=False)
    setting_correlations.to_csv(args.output_dir / "fd001_setting_sensor_correlations.csv", index=False)
    make_plots(metrics, deciles, correlations, args.output_dir / "figures")

    print("FD001 sensor analysis completed.")
    print(f"Training rows: {len(train):,}; engines: {train['unit_id'].nunique()}")
    print(f"Testing rows checked: {len(test):,}; engines: {test['unit_id'].nunique()}")
    print(f"Constant training sensors: {metrics.loc[metrics.constant, 'sensor'].tolist()}")
    print(f"Reports written to: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
