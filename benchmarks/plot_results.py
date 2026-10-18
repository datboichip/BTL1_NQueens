
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Load benchmark CSVs, including repeated runs.
files = [BASE_DIR / "solver_comparison.csv"]
files += sorted(BASE_DIR.glob("solver_comparison_run_*.csv"))
files = list(dict.fromkeys(f for f in files if f.exists()))

if not files:
    raise FileNotFoundError(
        f"No benchmark CSV files found in {BASE_DIR}"
    )

frames = []

for file in files:
    df = pd.read_csv(file)
    df["source_file"] = file.name
    frames.append(df)

data = pd.concat(frames, ignore_index=True)

# Support older CSV column names.
if "solve_time_seconds" not in data.columns:
    data["solve_time_seconds"] = (
        data["solve_time"]
        if "solve_time" in data.columns
        else float("nan")
    )

if "build_time_seconds" not in data.columns:
    data["build_time_seconds"] = float("nan")

if "elapsed_seconds" not in data.columns:
    data["elapsed_seconds"] = float("nan")

for column in [
    "n",
    "solve_time_seconds",
    "build_time_seconds",
    "elapsed_seconds",
]:
    data[column] = pd.to_numeric(data[column], errors="coerce")

data["status"] = data["status"].astype(str).str.upper()
data["solver"] = data["solver"].astype(str)

# Recognize successful results across the benchmark solvers.
success_statuses = {"SAT", "OPTIMAL", "FEASIBLE"}
timeout_statuses = {
    "TIMEOUT",
    "UNKNOWN_OR_TIMEOUT",
    "TIMELIMIT",
    "TIME_LIMIT",
}

data["is_success"] = data["status"].isin(success_statuses)
data["is_timeout"] = data["status"].isin(timeout_statuses)
data["is_error"] = data["status"].isin({"ERROR"})

# Runtime statistics use successful runs only.
successful = data[data["is_success"]].copy()

if successful.empty:
    raise ValueError(
        "No successful runs found. Check the status values in your CSVs."
    )

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

counts = (
    data.groupby(["n", "solver"])
    .agg(
        total_runs=("status", "size"),
        timeout_count=("is_timeout", "sum"),
        error_count=("is_error", "sum"),
    )
    .reset_index()
)

summary = summary.merge(
    counts, on=["n", "solver"], how="left"
)

summary["success_rate_percent"] = (
    summary["successful_runs"] / summary["total_runs"] * 100
)

summary.to_csv(
    RESULTS_DIR / "solver_summary.csv",
    index=False,
)

# Consistent solver order, including SCIP if present.
preferred_order = [
    "Glucose3 Pairwise",
    "Glucose3 Sequential",
    "OR-Tools CP-SAT",
    "SCIP MIP",
]
solvers = [s for s in preferred_order if s in data["solver"].unique()]
solvers += [
    s for s in data["solver"].unique() if s not in solvers
]


def plot_metric(column, ylabel, title, filename, logarithmic=False):
    plt.figure(figsize=(10, 6))
    plotted = False

    for solver_name in solvers:
        group = summary[summary["solver"] == solver_name]
        group = group.dropna(subset=[column]).sort_values("n")

        if group.empty:
            continue

        # Log scale cannot display zero or negative values.
        if logarithmic:
            group = group[group[column] > 0]

        if group.empty:
            continue

        plt.plot(
            group["n"],
            group[column],
            marker="o",
            label=solver_name,
        )
        plotted = True

    plt.xlabel("Board size (N)")
    plt.ylabel(ylabel)
    plt.title(title)

    if logarithmic:
        plt.yscale("log")

    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    if plotted:
        plt.legend()

    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename, dpi=300)
    plt.close()


# Chart 1: median solver runtime.
plot_metric(
    "median_solve_time",
    "Median solve time (seconds)",
    "N-Queens Solver Runtime Comparison",
    "runtime_comparison.png",
    logarithmic=True,
)

# Chart 2: median model/formula construction time.
plot_metric(
    "median_build_time",
    "Median build time (seconds)",
    "N-Queens Model Build Time Comparison",
    "build_time_comparison.png",
    logarithmic=True,
)

# Chart 3: number of timed-out runs.
timeout_data = (
    data.groupby(["n", "solver"])["is_timeout"]
    .sum()
    .reset_index(name="timeout_count")
)

plt.figure(figsize=(10, 6))

for solver_name in solvers:
    group = timeout_data[
        timeout_data["solver"] == solver_name
    ].sort_values("n")

    if not group.empty:
        plt.plot(
            group["n"],
            group["timeout_count"],
            marker="o",
            label=solver_name,
        )

plt.xlabel("Board size (N)")
plt.ylabel("Number of timed-out runs")
plt.title("Solver Timeouts by Board Size")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(RESULTS_DIR / "timeout_comparison.png", dpi=300)
plt.close()

print(f"Loaded {len(files)} CSV files:")
for file in files:
    print(f"  {file.name}")

print("\nSolvers found:")
for solver_name in solvers:
    print(f"  {solver_name}")

print(f"\nSummary and charts saved to: {RESULTS_DIR}")
