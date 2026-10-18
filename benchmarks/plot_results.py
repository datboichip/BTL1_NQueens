
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# All paths are relative to this script.
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Read the original CSV and all repeated-run CSV files.
files = [BASE_DIR / "solver_comparison.csv"]
files += sorted(BASE_DIR.glob("solver_comparison_run_*.csv"))
files = [f for f in files if f.exists()]

if not files:
    raise FileNotFoundError("No benchmark CSV files found.")

frames = []

for file in files:
    df = pd.read_csv(file)
    df["source_file"] = file.name
    frames.append(df)

data = pd.concat(frames, ignore_index=True)

# Normalize column names and support older benchmark outputs.
if "solve_time_seconds" not in data.columns:
    data["solve_time_seconds"] = (
        data["solve_time"] if "solve_time" in data.columns else float("nan")
    )

if "build_time_seconds" not in data.columns:
    data["build_time_seconds"] = float("nan")

if "elapsed_seconds" not in data.columns:
    data["elapsed_seconds"] = float("nan")

# Convert timing fields to numbers.
time_columns = [
    "solve_time_seconds",
    "build_time_seconds",
    "elapsed_seconds",
]

for col in time_columns:
    data[col] = pd.to_numeric(data[col], errors="coerce")

data["n"] = pd.to_numeric(data["n"], errors="coerce")
data["status"] = data["status"].astype(str).str.upper()

# Keep successful runs for runtime statistics.
successful = data[data["status"].isin(["SAT", "OPTIMAL", "FEASIBLE"])].copy()

if successful.empty:
    raise ValueError(
        "No successful runs found. Check the status column in your CSV files."
    )

# Summarize successful runtimes by board size and solver.
summary = (
    successful.groupby(["n", "solver"])
    .agg(
        successful_runs=("status", "count"),
        mean_solve_time=("solve_time_seconds", "mean"),
        median_solve_time=("solve_time_seconds", "median"),
        mean_build_time=("build_time_seconds", "mean"),
        median_build_time=("build_time_seconds", "median"),
        mean_total_time=("elapsed_seconds", "mean"),
        median_total_time=("elapsed_seconds", "median"),
    )
    .reset_index()
)

# Count timeouts and errors for each solver and board size.
failures = (
    data.assign(
        timed_out=data["status"].isin(["TIMEOUT", "UNKNOWN_OR_TIMEOUT"]),
        error=data["status"].eq("ERROR"),
    )
    .groupby(["n", "solver"])
    .agg(
        total_runs=("status", "size"),
        timeout_count=("timed_out", "sum"),
        error_count=("error", "sum"),
    )
    .reset_index()
)

summary = summary.merge(failures, on=["n", "solver"], how="left")
summary["success_rate_percent"] = (
    summary["successful_runs"] / summary["total_runs"] * 100
)

summary.to_csv(RESULTS_DIR / "solver_summary.csv", index=False)

# Chart 1: Median solve time vs board size.
plt.figure(figsize=(10, 6))

for solver, group in summary.groupby("solver"):
    group = group.sort_values("n")
    plt.plot(
        group["n"],
        group["median_solve_time"],
        marker="o",
        label=solver,
    )

plt.xlabel("Board size (N)")
plt.ylabel("Median solve time (seconds)")
plt.title("N-Queens Solver Runtime Comparison")
plt.yscale("log")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(RESULTS_DIR / "runtime_comparison.png", dpi=300)
plt.close()

# Chart 2: Median model build time vs board size.
build_data = summary.dropna(subset=["median_build_time"])

if not build_data.empty:
    plt.figure(figsize=(10, 6))

    for solver, group in build_data.groupby("solver"):
        group = group.sort_values("n")
        plt.plot(
            group["n"],
            group["median_build_time"],
            marker="o",
            label=solver,
        )

    plt.xlabel("Board size (N)")
    plt.ylabel("Median build time (seconds)")
    plt.title("N-Queens Model Build Time Comparison")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "build_time_comparison.png", dpi=300)
    plt.close()

# Chart 3: Timeout counts by solver and board size.
timeout_data = (
    data.assign(
        timed_out=data["status"].isin(["TIMEOUT", "UNKNOWN_OR_TIMEOUT"])
    )
    .groupby(["n", "solver"])["timed_out"]
    .sum()
    .reset_index(name="timeout_count")
)

plt.figure(figsize=(10, 6))

for solver, group in timeout_data.groupby("solver"):
    group = group.sort_values("n")
    plt.plot(
        group["n"],
        group["timeout_count"],
        marker="o",
        label=solver,
    )

plt.xlabel("Board size (N)")
plt.ylabel("Number of timeouts")
plt.title("Solver Timeouts by Board Size")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(RESULTS_DIR / "timeout_comparison.png", dpi=300)
plt.close()

print(f"Read {len(files)} CSV files:")
for file in files:
    print(f"  {file.name}")

print(f"\nSummary and charts saved in: {RESULTS_DIR}")
