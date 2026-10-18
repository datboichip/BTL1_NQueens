
"""Benchmark SAT, CP-SAT, and MIP solvers for N-Queens."""

import csv
import time
from pathlib import Path

from solvers.sat_solver import solve_nqueens
from solvers.cp_sat_solver import solve_n_queens as solve_cp
from solvers.scip_solver import solve_n_queens as solve_scip
# from solvers.mip_solver import solve_n_queens as solve_mip


SIZES = range(4, 65, 4)
TIME_LIMIT = 40

RUN_ID = 1  # Change to 2, 3, 4, or 5 for each run
OUTPUT = Path(__file__).with_name(f"solver_comparison_run_{RUN_ID}.csv")

def run_sat(n, encoding):
    return solve_nqueens(
        n,
        encoding=encoding,
        solver_name="glucose3",
        time_limit=TIME_LIMIT,
    )


def run_and_record(name, solve, n):
    start = time.perf_counter()

    try:
        result = solve(n)
        elapsed = time.perf_counter() - start

        return {
            "n": n,
            "solver": name,
            "status": result.get("status", "UNKNOWN"),
            "build_time_seconds": result.get(
                "build_time_seconds", ""
            ),
            "solve_time_seconds": result.get(
                "solve_time_seconds",
                result.get("solve_time", ""),
            ),
            "elapsed_seconds": round(elapsed, 6),
            "timeout_seconds": TIME_LIMIT,
            "error": "",
        }

    except Exception as exc:
        return {
            "n": n,
            "solver": name,
            "status": "ERROR",
            "build_time_seconds": "",
            "solve_time_seconds": "",
            "elapsed_seconds": round(
                time.perf_counter() - start, 6
            ),
            "timeout_seconds": TIME_LIMIT,
            "error": str(exc),
        }


def main():
    methods = [
        (
            "Glucose3 Pairwise",
            lambda n: run_sat(n, "pairwise"),
        ),
        (
            "Glucose3 Sequential",
            lambda n: run_sat(n, "sequential"),
        ),
        (
            "OR-Tools CP-SAT",
            lambda n: solve_cp(n, time_limit=TIME_LIMIT),
        ),
        (
            "SCIP MIP",
            lambda n: solve_scip(n, time_limit=TIME_LIMIT),
        ),
    ]

    fields = [
        "n",
        "solver",
        "status",
        "build_time_seconds",
        "solve_time_seconds",
        "elapsed_seconds",
        "timeout_seconds",
        "error",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for n in SIZES:
            for name, solve in methods:
                print(f"Running {name}, N={n}...", flush=True)

                row = run_and_record(name, solve, n)
                writer.writerow(row)
                file.flush()

                print(
                    f"  Status: {row['status']}, "
                    f"elapsed: {row['elapsed_seconds']}s",
                    flush=True,
                )

    print(f"\nResults saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
