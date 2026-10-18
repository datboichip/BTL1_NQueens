
import time
import gurobipy as gp
from gurobipy import GRB


def solve_n_queens(n, time_limit=40):
    model = gp.Model("n_queens")
    model.Params.OutputFlag = 0
    model.Params.TimeLimit = time_limit

    x = model.addVars(n, n, vtype=GRB.BINARY, name="q")

    # Exactly one queen in each row.
    for r in range(n):
        model.addConstr(gp.quicksum(x[r, c] for c in range(n)) == 1)

    # Exactly one queen in each column.
    for c in range(n):
        model.addConstr(gp.quicksum(x[r, c] for r in range(n)) == 1)

    # At most one queen on each diagonal.
    for d in range(-(n - 1), n):
        model.addConstr(
            gp.quicksum(
                x[r, c]
                for r in range(n)
                for c in range(n)
                if r - c == d
            ) <= 1
        )

    for s in range(2 * n - 1):
        model.addConstr(
            gp.quicksum(
                x[r, c]
                for r in range(n)
                for c in range(n)
                if r + c == s
            ) <= 1
        )

    start = time.perf_counter()
    model.optimize()
    solve_time = time.perf_counter() - start

    if model.SolCount > 0:
        solution = [
            next(c for c in range(n) if x[r, c].X > 0.5)
            for r in range(n)
        ]
        result_status = "SAT"
    elif model.Status == GRB.INFEASIBLE:
        solution = None
        result_status = "UNSAT"
    elif model.Status == GRB.TIME_LIMIT:
        solution = None
        result_status = "UNKNOWN_OR_TIMEOUT"
    else:
        solution = None
        result_status = "OTHER"

    model.dispose()

    return {
        "n": n,
        "solver": "Gurobi MIP",
        "status": result_status,
        "solve_time": solve_time,
        "solution": solution,
    }


if __name__ == "__main__":
    for n in [8, 16, 32, 40, 48, 56, 64]:
        print(solve_n_queens(n))
