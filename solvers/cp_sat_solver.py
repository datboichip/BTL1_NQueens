
import time
from ortools.sat.python import cp_model


def solve_n_queens(n, time_limit=40):
    model = cp_model.CpModel()

    # col[r] is the column occupied by the queen in row r.
    col = [
        model.new_int_var(0, n - 1, f"q_{r}")
        for r in range(n)
    ]

    model.add_all_different(col)

    # Queens cannot share either diagonal.
    model.add_all_different([
        col[r] + r for r in range(n)
    ])
    model.add_all_different([
        col[r] - r for r in range(n)
    ])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit

    start = time.perf_counter()
    status = solver.solve(model)
    solve_time = time.perf_counter() - start

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solution = [solver.value(col[r]) for r in range(n)]
        result_status = "SAT"
    elif status == cp_model.INFEASIBLE:
        solution = None
        result_status = "UNSAT"
    else:
        solution = None
        result_status = "UNKNOWN_OR_TIMEOUT"

    return {
        "n": n,
        "solver": "OR-Tools CP-SAT",
        "status": result_status,
        "solve_time": solve_time,
        "solution": solution,
    }


if __name__ == "__main__":
    for n in [8, 16, 32, 40, 48, 56, 64]:
        print(solve_n_queens(n))
