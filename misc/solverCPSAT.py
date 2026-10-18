"""Optional OR-Tools CP-SAT comparison solver."""

from time import perf_counter


def solve_cpsat(n: int):
    try:
        from ortools.sat.python import cp_model
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional dependency with: pip install ortools"
        ) from exc

    start = perf_counter()

    model = cp_model.CpModel()

    # queens[r] is the column containing the queen in row r.
    queens = [
        model.NewIntVar(0, n - 1, f"q_{r}")
        for r in range(n)
    ]

    # No two queens share a column.
    model.AddAllDifferent(queens)

    # No two queens share a diagonal.
    model.AddAllDifferent([
        queens[r] + r for r in range(n)
    ])
    model.AddAllDifferent([
        queens[r] - r for r in range(n)
    ])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    elapsed = perf_counter() - start
    feasible = status in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE,
    )

    positions = (
        [(r, solver.Value(queens[r])) for r in range(n)]
        if feasible
        else []
    )

    return {
        "n": n,
        "satisfiable": feasible,
        "positions": positions,
        "solve_time_seconds": elapsed,
        "solver": "OR-Tools CP-SAT",
    }
