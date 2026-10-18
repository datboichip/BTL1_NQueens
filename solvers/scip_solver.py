
import time
from pyscipopt import Model, quicksum


def solve_n_queens(n, time_limit=40):
    build_start = time.perf_counter()

    model = Model("N_Queens")
    model.hideOutput()

    x = {
        (r, c): model.addVar(vtype="B", name=f"q_{r}_{c}")
        for r in range(n)
        for c in range(n)
    }

    # Exactly one queen per row.
    for r in range(n):
        model.addCons(
            quicksum(x[r, c] for c in range(n)) == 1
        )

    # Exactly one queen per column.
    for c in range(n):
        model.addCons(
            quicksum(x[r, c] for r in range(n)) == 1
        )

    # At most one queen on each diagonal.
    for diff in range(-(n - 1), n):
        diagonal = [
            x[r, c]
            for r in range(n)
            for c in range(n)
            if r - c == diff
        ]
        if len(diagonal) > 1:
            model.addCons(quicksum(diagonal) <= 1)

    for total in range(2 * n - 1):
        diagonal = [
            x[r, c]
            for r in range(n)
            for c in range(n)
            if r + c == total
        ]
        if len(diagonal) > 1:
            model.addCons(quicksum(diagonal) <= 1)

    build_time = time.perf_counter() - build_start

    model.setParam("limits/time", float(time_limit))

    solve_start = time.perf_counter()
    model.optimize()
    solve_time = time.perf_counter() - solve_start

    scip_status = str(model.getStatus()).lower()
    solution = None

    if model.getNSols() > 0:
        best = model.getBestSol()
        solution = [
            next(
                c for c in range(n)
                if model.getSolVal(best, x[r, c]) > 0.5
            )
            for r in range(n)
        ]
        result_status = "SAT"
    elif scip_status == "infeasible":
        result_status = "UNSAT"
    elif scip_status in {
        "timelimit", "userinterrupt", "memlimit"
    }:
        result_status = "TIMEOUT"
    else:
        result_status = "UNKNOWN"

    return {
        "n": n,
        "solver": "SCIP MIP",
        "status": result_status,
        "scip_status": scip_status,
        "build_time_seconds": build_time,
        "solve_time_seconds": solve_time,
        "solve_time": solve_time,
        "solution": solution,
    }


if __name__ == "__main__":
    for n in [8, 16, 32, 40, 48, 56, 64]:
        result = solve_n_queens(n, time_limit=40)
        print(
            f"N={n}: {result['status']}, "
            f"build={result['build_time_seconds']:.6f}s, "
            f"solve={result['solve_time_seconds']:.6f}s"
        )

