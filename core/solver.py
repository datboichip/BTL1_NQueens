"""PySAT solver wrapper."""

from time import perf_counter
from pysat.solvers import Solver

from core.encoderCustom import build_clauses as build_pairwise
from core.encoderPySATDefault import build_clauses as build_pysat


SUPPORTED_SOLVERS = [
    "glucose3",
    "g4",
    "minisat22",
    "cadical153",
]


def solve_nqueens(
    n: int,
    encoding: str = "sequential",
    solver_name: str = "glucose3",
) -> dict:
    # Build the CNF formula.
    start_build = perf_counter()

    if encoding == "pairwise":
        clauses = build_pairwise(n)
    elif encoding == "sequential":
        clauses = build_pysat(n, "sequential")
    else:
        raise ValueError(
            "encoding must be 'pairwise' or 'sequential'"
        )

    build_time = perf_counter() - start_build

    # Solve the SAT instance.
    start_solve = perf_counter()

    with Solver(
        name=solver_name,
        bootstrap_with=clauses,
    ) as solver:
        satisfiable = solver.solve()
        model = solver.get_model() if satisfiable else None

    solve_time = perf_counter() - start_solve

    # Convert positive SAT variables into queen positions.
    positions = []

    if model:
        positive = {lit for lit in model if lit > 0}

        for r in range(n):
            for c in range(n):
                variable = r * n + c + 1
                if variable in positive:
                    positions.append((r, c))

    return {
        "n": n,
        "satisfiable": satisfiable,
        "positions": positions,
        "clauses": len(clauses),
        "variables_base": n * n,
        "build_time_seconds": build_time,
        "solve_time_seconds": solve_time,
        "solver": solver_name,
        "encoding": encoding,
    }
